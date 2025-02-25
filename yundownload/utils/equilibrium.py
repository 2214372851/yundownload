import math
import random
import collections
import time
import statistics
import asyncio
from yundownload.utils.logger import logger


class DynamicConcurrencyController:
    """
    Dynamic concurrency control classes
    """
    def __init__(self, min_concurrency=1, max_concurrency=30, window_size=100):
        # 并发控制参数
        self.min_concurrency = min_concurrency
        self.max_concurrency = max_concurrency
        self.current_concurrency = min_concurrency
        self.last_adjustment = time.monotonic()

        # 指标采样窗口
        self.window_size = window_size
        self.response_times = collections.deque(maxlen=window_size)
        self.successes = collections.deque(maxlen=window_size)
        self.failures = collections.deque(maxlen=window_size)

        # 状态跟踪
        self.base_response_time = None
        self.last_throughput = 0
        self.stability_counter = 0

        # 平滑处理参数
        self.ema_alpha = 0.3
        self.ema_response = 0

        # 信号量
        self.semaphore = asyncio.Semaphore(min_concurrency)

    def record_result(self, response_time: None, success=True):
        """记录每次请求的结果"""
        if response_time:
            self.response_times.append(response_time)
        if success:
            self.successes.append(1)
        else:
            self.failures.append(1)

        # 动态校准基准响应时间
        self._calibrate_base_response_time()

    def calculate_concurrency(self):
        """计算新的并发数值"""
        if len(self.response_times) < 10:  # 冷启动阶段
            return self._linear_ramp_up()

        # 核心指标计算
        success_rate = self._calculate_success_rate()
        rt_factor = self._calculate_response_time_factor()
        load_factor = self._calculate_load_factor()

        # 动态调整公式
        new_concurrency = self.current_concurrency * (
                (success_rate ** 1.5) *
                (rt_factor ** 0.7) *
                (load_factor ** 0.5)
        )

        # 应用自适应策略
        new_concurrency = self._apply_adaptive_policies(new_concurrency)

        # 边界保护和阻尼处理
        new_concurrency = max(self.min_concurrency,
                              min(self.max_concurrency, new_concurrency))
        new_concurrency = self._dampen_adjustment(new_concurrency)

        self.current_concurrency = new_concurrency
        return round(new_concurrency)

    def _calibrate_base_response_time(self):
        """动态校准基准响应时间（使用statistics替代numpy）"""
        if len(self.response_times) > 20:
            recent_rt = list(self.response_times)[-20:]
            try:
                new_base = statistics.median(recent_rt)
            except statistics.StatisticsError:
                new_base = recent_rt[len(recent_rt) // 2] if recent_rt else 0

            if self.base_response_time is None:
                self.base_response_time = new_base
            else:
                # 平滑过渡校准
                self.base_response_time = 0.8 * self.base_response_time + 0.2 * new_base

    def _calculate_success_rate(self):
        """计算加权成功率"""
        total = len(self.successes) + len(self.failures)
        if total == 0:
            return 1.0
        recent_success = sum(list(self.successes)[-10:]) / 10 if len(self.successes) >= 10 else 1.0
        historical_success = sum(self.successes) / total
        return 0.7 * recent_success + 0.3 * historical_success

    def _calculate_response_time_factor(self):
        """计算响应时间影响因子"""
        # EMA平滑处理响应时间
        current_rt = statistics.mean(self.response_times) if self.response_times else 0
        self.ema_response = (self.ema_alpha * current_rt +
                             (1 - self.ema_alpha) * self.ema_response)

        if self.base_response_time is None or self.base_response_time < 1e-5:
            return 1.0

        # 非线性响应关系
        rt_ratio = self.ema_response / self.base_response_time
        return 1.0 / (1.0 + math.log(max(1.0, rt_ratio)))

    def _calculate_load_factor(self):
        """计算系统负载因子"""
        throughput = len(self.successes) / (time.monotonic() - self.last_adjustment + 1e-7)
        throughput_ratio = throughput / (self.last_throughput + 1e-7)
        self.last_throughput = throughput

        return max(0.8, min(1.2, throughput_ratio))

    def _apply_adaptive_policies(self, concurrency):
        """应用自适应控制策略"""
        # 快速失败保护
        if len(self.failures) > len(self.successes):
            return concurrency * 0.5

        # 响应时间突增保护
        if len(self.response_times) > 30:
            recent_rt = statistics.mean(list(self.response_times)[-10:])
            if recent_rt > 3 * self.base_response_time:
                return concurrency * 0.7

        # 稳定性奖励
        if abs(concurrency - self.current_concurrency) < 0.1 * self.current_concurrency:
            self.stability_counter += 1
            if self.stability_counter > 5:
                return min(concurrency * 1.1, self.max_concurrency)
        else:
            self.stability_counter = 0

        return concurrency

    def _dampen_adjustment(self, new_concurrency):
        """调整阻尼系数避免震荡"""
        delta = new_concurrency - self.current_concurrency
        max_delta = 0.3 * self.current_concurrency  # 单次最大变化30%
        dampened_delta = max(-max_delta, min(delta, max_delta))
        return self.current_concurrency + dampened_delta

    def _linear_ramp_up(self):
        """冷启动阶段线性增长"""
        if time.monotonic() - self.last_adjustment > 5.0:  # 每5秒增长一次
            self.current_concurrency = min(self.current_concurrency + 1, self.max_concurrency)
            self.last_adjustment = time.monotonic()
        return self.current_concurrency

    def get_current_concurrency(self):
        """获取当前并发数"""
        return round(self.current_concurrency)

    def __len__(self):
        return self.calculate_concurrency()


class DynamicSemaphore(asyncio.Semaphore):
    """
    Dynamic control of concurrent semaphores
    """
    def __init__(self, dcc: 'DynamicConcurrencyController'):
        initial_permits = len(dcc)
        self._dcc = dcc
        super().__init__(value=initial_permits)
        self._target = initial_permits  # 当前目标并发数
        self._lock = asyncio.Lock()  # 状态修改锁

    async def adaptive_update(self):
        """动态调整信号量容量（线程安全）"""
        new_target = self._dcc.calculate_concurrency()
        if new_target == self._target:
            return
        await self.update(new_target)

    async def update(self, new_target: int):
        """动态调整信号量容量（线程安全）"""
        async with self._lock:
            logger.info(f"❤️Adjusting concurrency from {self._target} to {new_target}")
            if new_target < 0:
                raise ValueError("Concurrency cannot be negative")

            delta = new_target - self._target
            self._target = new_target

            # 调整可用许可数量
            if delta > 0:
                # 扩容：增加可用许可
                self._value += delta
                # 唤醒等待者（最多唤醒delta个）
                for _ in range(min(delta, len(self._waiters))):
                    self._wake_up_next()
            elif delta < 0:
                # 缩容：减少可用许可（不影响已获取许可）
                self._value = max(0, self._value + delta)

    @property
    def current_target(self):
        """获取当前目标并发数"""
        return self._target

    @property
    def available_permits(self):
        """获取当前可用许可数"""
        return self._value

    def record_result(self, rt: float = None, success: bool = True):
        self._dcc.record_result(rt, success)
