"""New UI recognition and safe mouse-command transitions, without game input."""
from pathlib import Path
import sys, unittest
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from circular import CircularReader,CircularReading,CircularCommand,KeyPromptCommand


def frame(width=1920,height=1072,hold=True,center=None):
    radius=166*height/1072
    cx,cy=center or (round(width*.772),round(height*.537))
    scale=radius/166
    rgb=np.full((height,width,3),(28,80,150),dtype=np.uint8)
    patch=cv2.cvtColor(cv2.imread(str(ROOT/'tests/fixtures/circular_ui.png')),cv2.COLOR_BGR2RGB)
    size=round(360*scale);patch=cv2.resize(patch,(size,size))
    left,top=round(cx-size/2),round(cy-size/2)
    rgb[top:top+size,left:left+size]=patch
    key='hold' if hold else 'release'
    glyph=cv2.imread(str(ROOT/f'src/assets/circle_{key}.png'),cv2.IMREAD_GRAYSCALE)
    glyph=cv2.resize(glyph,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    left,top=round(cx-16*scale),round(cy-318*scale)
    area=rgb[top:top+glyph.shape[0],left:left+glyph.shape[1]]
    area[glyph>0]=235
    return rgb


class CircularTests(unittest.TestCase):
    def key_frame(self,count=2,side='A'):
        image=frame();cx,cy=round(1920*.772),round(1072*.537)
        patch=cv2.cvtColor(cv2.imread(str(ROOT/'tests/fixtures/circular_key_a.png')),cv2.COLOR_BGR2RGB)
        if count==1:patch[110:130,59:78]=(28,80,150)
        x=cx+(-274 if side=='A' else 274)
        image[cy-60:cy+80,x-55:x+55]=patch
        return image

    def test_real_two_dot_prompt_and_one_dot_variant(self):
        for count in (1,2):
            reader=CircularReader(ROOT/'src/assets')
            reading=reader.read(self.key_frame(count))
            self.assertEqual((reading.key,reading.presses),('A',count))

    def test_active_side_and_prompt_scaling(self):
        for side in ('A','D'):
            source=self.key_frame(side=side)
            for size in ((1920,1072),(1280,715),(800,447)):
                reader=CircularReader(ROOT/'src/assets')
                reading=reader.read(cv2.resize(source,size,interpolation=cv2.INTER_AREA))
                self.assertIsNotNone(reading,size)
                self.assertEqual((reading.key,reading.presses),(side,2),(side,size))

    def test_inactive_card_and_conflicting_prompts_are_ignored(self):
        reader=CircularReader(ROOT/'src/assets')
        self.assertIsNone(reader.read(frame()).key)
        image=self.key_frame(side='A');other=self.key_frame(side='D')
        image[:,1650:]=other[:,1650:]
        self.assertIsNone(reader.read(image).key)

    def test_key_event_is_not_repeated_on_every_video_frame(self):
        command=KeyPromptCommand()
        reading=CircularReading((1,1),1,1.,key='A',presses=2)
        self.assertEqual(command.step(reading,0),['A'])
        self.assertEqual(command.step(reading,.05),[])
        reading.presses=1
        self.assertEqual(command.step(reading,.11),['A'])
        self.assertEqual(command.step(reading,.4),[])
        reading.key=None
        self.assertEqual(command.step(reading,.5),[])
        self.assertEqual(command.step(reading,.8),[])
        reading.key='D';reading.presses=1
        self.assertEqual(command.step(reading,.9),['D'])
        self.assertEqual(command.step(None,1),[])

    def test_arrows_with_marker_outside_or_at_edge(self):
        for held in (True,False):
            reader=CircularReader(ROOT/'src/assets')
            reading=reader.read(frame(hold=held))
            self.assertIsNotNone(reading)
            self.assertEqual(reading.hold,held)
            self.assertFalse(reading.complete)

    def test_resize_and_relocate_reacquires(self):
        reader=CircularReader(ROOT/'src/assets')
        for width,height,center in ((1920,1072,None),(800,599,(550,350)),(1280,720,(700,380))):
            reading=reader.read(frame(width,height,False,center))
            self.assertIsNotNone(reading,(width,height))
            self.assertEqual(reading.hold,False)
            expected=center or (width*.772,height*.537)
            self.assertLess(abs(reading.center[0]-expected[0]),10)

    def test_green_map_and_detached_arrow_do_not_issue_commands(self):
        reader=CircularReader(ROOT/'src/assets')
        for color in ((20,220,50),(24,100,150),(0,0,0)):
            image=np.full((599,800,3),color,dtype=np.uint8)
            cv2.putText(image,'^^',(590,140),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)
            self.assertIsNone(reader.read(image))

    def test_arrow_is_latched_only_while_ui_is_present(self):
        command=CircularCommand()
        reading=CircularReading((1,1),1,1.,hold=True)
        self.assertTrue(command.step(reading,1))
        reading.hold=None
        self.assertTrue(command.step(reading,1.5))
        self.assertTrue(command.step(None,1.6))
        self.assertFalse(command.step(None,1.7))
        self.assertFalse(command.step(reading,2))
        reading.hold=True
        self.assertTrue(command.step(reading,2.1))
        reading.complete=True
        self.assertFalse(command.step(reading,2.2))


if __name__=='__main__':unittest.main()
