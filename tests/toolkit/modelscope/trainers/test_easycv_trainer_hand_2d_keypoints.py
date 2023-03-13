# Copyright (c) Alibaba, Inc. and its affiliates.
import glob
import os
import shutil
import tempfile
import unittest

import torch
from modelscope.msdatasets import MsDataset
from modelscope.trainers import build_trainer
from modelscope.utils.constant import DownloadMode, LogKeys
from modelscope.utils.logger import get_logger
from modelscope.utils.test_utils import test_level

from easycv.toolkit import modelscope


@unittest.skipIf(not torch.cuda.is_available(), 'cuda unittest')
class EasyCVTrainerTestHand2dKeypoints(unittest.TestCase):
    model_id = 'damo/cv_hrnetw18_hand-pose-keypoints_coco-wholebody'

    def setUp(self):
        self.logger = get_logger()
        self.logger.info(
            ('Testing %s.%s' % (type(self).__name__, self._testMethodName)))
        self.tmp_dir = tempfile.TemporaryDirectory().name
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _train(self):
        cfg_options = {'train.max_epochs': 20}

        trainer_name = 'easycv'

        train_dataset = MsDataset.load(
            dataset_name='cv_hand_2d_keypoints_coco_wholebody',
            namespace='chenhyer',
            split='subtrain',
            download_mode=DownloadMode.FORCE_REDOWNLOAD)
        eval_dataset = MsDataset.load(
            dataset_name='cv_hand_2d_keypoints_coco_wholebody',
            namespace='chenhyer',
            split='subtrain',
            download_mode=DownloadMode.FORCE_REDOWNLOAD)

        kwargs = dict(
            model=self.model_id,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            work_dir=self.tmp_dir,
            cfg_options=cfg_options)

        trainer = build_trainer(trainer_name, kwargs)
        trainer.train()

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_trainer_single_gpu(self):
        self._train()

        results_files = os.listdir(self.tmp_dir)
        json_files = glob.glob(os.path.join(self.tmp_dir, '*.log.json'))
        self.assertEqual(len(json_files), 1)
        self.assertIn(f'{LogKeys.EPOCH}_10.pth', results_files)
        self.assertIn(f'{LogKeys.EPOCH}_20.pth', results_files)


if __name__ == '__main__':
    unittest.main()
