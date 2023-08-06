import shutil
import unittest
from pathlib import Path

from submerger.test.execute_command import execute_command

TEST_DATA_PATH = Path('submerger/test/data')
TEST_OUTPUT_PATH = Path('test_outputs')
DUALSUB_EXPECTED_PATH = TEST_DATA_PATH / 'dualsub_expected.srt'
TEST_GLOBAL_MERGING_PATH = TEST_DATA_PATH / 'global_merging'
NUMBER_OF_EPISODES = 3


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        TEST_OUTPUT_PATH.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(TEST_OUTPUT_PATH)
        for i in range(1, NUMBER_OF_EPISODES + 1):
            Path.unlink(TEST_GLOBAL_MERGING_PATH /
                        f'ep{i}.srt', missing_ok=True)

    async def test_submerger_from_srt(self) -> None:
        dualsub_from_srt_path = TEST_OUTPUT_PATH / 'dualsub_from_srt.srt'

        return_code, _, _ = await execute_command(
            'submerge',
            '--subtitles', TEST_DATA_PATH / 'eng.srt', TEST_DATA_PATH / 'ger.srt',
            '--output', dualsub_from_srt_path,
        )
        self.assertEqual(return_code, 0)

        with (open(dualsub_from_srt_path, encoding='utf-8')
                as dualsub_from_srt,
                open(DUALSUB_EXPECTED_PATH, encoding='utf-8')
                as dualsub_expected):
            self.assertEqual(dualsub_from_srt.read(),
                             dualsub_expected.read())

    async def test_submerger_from_video(self) -> None:
        dualsub_from_video_path = TEST_OUTPUT_PATH / 'dualsub_from_video.srt'
        video_path = TEST_DATA_PATH / 'vid.mp4'

        return_code, _, _ = await execute_command(
            'submerge',
            '--video', video_path,
            '--language', 'eng', 'ger',
            '--output', dualsub_from_video_path,
        )

        self.assertEqual(return_code, 0)

        with (open(dualsub_from_video_path, encoding='utf-8')
                as dualsub_from_video,
                open(DUALSUB_EXPECTED_PATH, encoding='utf-8')
                as dualsub_expected):
            self.assertEqual(dualsub_from_video.read(),
                             dualsub_expected.read())

    async def test_submerger_global(self) -> None:
        '''
            ep1: extraction from the subdirectory
            ep2: extraction from video file
            ep3: extraction from local directory
            ep4: missing subtitles
        '''

        expected_stdout = '''No eng subtitles for ep4
No ger subtitles for ep4

'''
        return_code, stdout, _ = await execute_command(
            'submerge',
            '--global',
            '--directory', TEST_GLOBAL_MERGING_PATH,
            '--language', 'eng', 'ger',
        )
        self.assertEqual(return_code, 0)
        self.assertEqual(stdout, expected_stdout)

        for episode_number in range(1, NUMBER_OF_EPISODES + 1):
            with (open(TEST_GLOBAL_MERGING_PATH / f'ep{episode_number}.srt', encoding='utf-8')
                  as actual_dualsub_srt,
                  open(TEST_GLOBAL_MERGING_PATH /
                       f'ep{episode_number}_expected.srt', encoding='utf-8')
                  as expected_dualsub_srt):
                self.assertEqual(actual_dualsub_srt.read(),
                                 expected_dualsub_srt.read())
