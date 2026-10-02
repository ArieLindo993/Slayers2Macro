import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from item_history import RewardReader


class FakeOCR:
    def __init__(self):self.calls=0

    def __call__(self,image,use_cls=False):
        self.calls+=1
        if float(image.mean())<40:return None,None
        # Reward text is present only in the second independently anchored crop.
        return [
            ([[210,120],[610,120],[610,175],[210,175]],'Clown Fish',.99),
            ([[650,178],[760,178],[760,220],[650,220]],'x1',.96),
        ],None


class RewardReaderFallback(unittest.TestCase):
    def test_independent_anchor_can_recognize_reward_after_badge_crop_fails(self):
        reader=RewardReader();reader.reader=FakeOCR()
        primary=np.zeros((420,650,3),dtype=np.uint8)
        fallback=np.full((420,650,3),80,dtype=np.uint8)

        payload=reader.read_with_diagnostics(primary,fallback)

        self.assertEqual(payload['reading']['name'],'Clown Fish')
        self.assertEqual(payload['reading']['quantity'],1)
        self.assertTrue(payload['reading']['name_validated'])
        debug=payload['__ocr_debug__']
        self.assertEqual(len(debug['recortes_ocr']),2)
        self.assertEqual(debug['recortes_ocr'][0]['caixas'],0)
        self.assertGreater(debug['recortes_ocr'][1]['caixas'],0)
        self.assertNotIn('Clown Fish',str(debug))

    def test_duplicate_crop_is_not_processed_twice(self):
        reader=RewardReader();fake=FakeOCR();reader.reader=fake
        crop=np.zeros((420,650,3),dtype=np.uint8)
        payload=reader.read_with_diagnostics(crop,crop.copy())
        self.assertEqual(fake.calls,1)
        self.assertEqual(len(payload['__ocr_debug__']['recortes_ocr']),1)


if __name__=='__main__':unittest.main()
