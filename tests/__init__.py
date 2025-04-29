from yundownload import Downloader, Resources

if __name__ == '__main__':
    with Downloader(max_workers=10) as d:
        result = d.submit(Resources(
            uri="https://physionet.org/static/published-projects/challenge-2020/classification-of-12-lead-ecgs-the-physionetcomputing-in-cardiology-challenge-2020-1.0.2.zip",
            save_path=r"./classification-of-12-lead-ecgs-the-physionetcomputing-in-cardiology-challenge-2020-1.0.2.zip",
            retry=30,
            retry_delay=(10, 30)
        ))
        assert result.result().is_success()