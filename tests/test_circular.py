"""New UI recognition and safe mouse-command transitions, without game input."""
from pathlib import Path
import sys, unittest
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from circular import CircularReader,CircularReading,CircularCommand,KeyPromptCommand


def frame(width=1920,height=1072,button='right',center=None):
    radius=166*height/1072
    cx,cy=center or (round(width*.772),round(height*.537))
    scale=radius/166
    rgb=np.full((height,width,3),(28,80,150),dtype=np.uint8)
    fixture='circular_green_cue.png' if button=='right' else 'circular_red_cue.png'
    patch=cv2.cvtColor(cv2.imread(str(ROOT/'tests/fixtures'/fixture)),cv2.COLOR_BGR2RGB)
    pw,ph=round(520*scale),round(440*scale);patch=cv2.resize(patch,(pw,ph))
    left,top=round(cx-260*scale),round(cy-260*scale)
    rgb[top:top+ph,left:left+pw]=patch
    key='hold' if button=='right' else 'release'
    glyph=cv2.imread(str(ROOT/f'src/assets/circle_{key}.png'),cv2.IMREAD_GRAYSCALE)
    glyph=cv2.resize(glyph,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    left,top=round(cx-16*scale),round(cy-318*scale)
    area=rgb[top:top+glyph.shape[0],left:left+glyph.shape[1]]
    area[glyph>0]=235
    return rgb


class CircularTests(unittest.TestCase):
    def test_white_arrows_are_ignored_and_position_controls_green_arc(self):
        image=frame()
        cx,cy=round(1920*.772),round(1072*.537)
        yy,xx=np.ogrid[:1072,:1920]
        distance=np.hypot(xx-cx,yy-cy)
        image[(distance>166*1.14)&(distance<166*1.55)]=(28,80,150)
        reader=CircularReader(ROOT/'src/assets')
        result=reader.read(image)
        self.assertIsNotNone(result);self.assertIsNone(result.mouse_button)
        command=CircularCommand()
        self.assertEqual(command.step(CircularReading((1,1),1,1,marker=-.25),0),'right')
        self.assertEqual(command.step(CircularReading((1,1),1,1,mouse_button='right'),.1),'right')
        self.assertEqual(command.step(CircularReading((1,1),1,1,marker=.02),.2),'right')
        self.assertEqual(CircularCommand().step(CircularReading((1,1),1,1,marker=.25),.2),'left')

    def test_left_button_instruction_overrides_position_and_remains_latched(self):
        command=CircularCommand()
        reading=CircularReading((1,1),1,1,mouse_button='left',marker=-.01,target=0.,band=.10)
        self.assertEqual(command.step(reading,0.),'left')
        reading.marker=-.01
        self.assertEqual(command.step(reading,.1),'left')
        reading.marker=.015;reading.mouse_button='right'
        self.assertEqual(command.step(reading,.2),'right')
        reading.marker=.02;reading.mouse_button=None
        self.assertEqual(command.step(reading,.3),'right')
        reading.mouse_button='left'
        self.assertEqual(command.step(reading,.4),'left')

    def test_marker_across_angle_wrap_takes_shortest_direction(self):
        command=CircularCommand()
        reading=CircularReading((1,1),1,1,marker=.49,target=-.49,band=.1)
        self.assertEqual(command.step(reading,0.),'right')
        reading.marker=-.46;reading.target=.49
        self.assertEqual(command.step(reading,.1),'left')

    def test_red_is_an_active_left_input_near_centre(self):
        for marker in (-.02,0.,.02):
            reading=CircularReading((1,1),1,1,mouse_button='left',marker=marker,target=.035,band=.15)
            self.assertEqual(CircularCommand().step(reading,0.),'left')

    def test_pressure_pauses_near_green_edge_and_resumes_without_chattering(self):
        for button,sign in (('right',1),('left',-1)):
            command=CircularCommand()
            reading=CircularReading((1,1),1,1,mouse_button=button,marker=0.,target=0.,band=.2)
            self.assertEqual(command.step(reading,0.),button)
            reading.marker=sign*.08
            self.assertIsNone(command.step(reading,.1))
            self.assertEqual(command.reason,'green_edge')
            reading.marker=sign*.06
            self.assertIsNone(command.step(reading,.2))
            reading.marker=None
            self.assertIsNone(command.step(reading,.3))
            reading.marker=sign*.02
            self.assertEqual(command.step(reading,.4),button)

    def test_new_direction_can_pull_back_from_unsafe_edge(self):
        command=CircularCommand()
        reading=CircularReading((1,1),1,1,mouse_button='right',marker=.13,target=0.,band=.2)
        self.assertIsNone(command.step(reading,0.))
        reading.mouse_button='left'
        self.assertEqual(command.step(reading,.1),'left')

    def test_recorded_red_at_centre_selects_left_button(self):
        rgb=np.full((1072,1920,3),30,np.uint8)
        crop=cv2.cvtColor(cv2.imread(str(ROOT/'tests/fixtures/circular_red_centre.png')),cv2.COLOR_BGR2RGB)
        rgb[316:756,1222:1742]=crop
        reading=CircularReader(ROOT/'src/assets').read(rgb)
        self.assertIsNotNone(reading);self.assertEqual(reading.mouse_button,'left')
        self.assertLess(reading.marker,reading.target)
        self.assertEqual(CircularCommand().step(reading,0.),'left')

    def test_coloured_cues_work_when_marker_is_temporarily_missing(self):
        reader=CircularReader(ROOT/'src/assets')
        cx,cy=round(1920*.772),round(1072*.537)
        for button in ('right','left'):
            self.assertEqual(reader.read_mouse_cue(frame(button=button),cx,cy,166,None),button)

    def test_coloured_cues_rotate_with_marker(self):
        reader=CircularReader(ROOT/'src/assets')
        cx,cy=round(1920*.772),round(1072*.537)
        for button in ('right','left'):
            for degrees in (-90,45,90):
                image=frame(button=button)
                rotated=cv2.warpAffine(image,cv2.getRotationMatrix2D((cx,cy),-degrees,1),(1920,1072))
                self.assertEqual(reader.read_mouse_cue(rotated,cx,cy,166,None),button,(button,degrees))

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
        for button in ('right','left'):
            reader=CircularReader(ROOT/'src/assets')
            reading=reader.read(frame(button=button))
            self.assertIsNotNone(reading)
            self.assertEqual(reading.mouse_button,button)
            self.assertFalse(reading.complete)

    def test_resize_and_relocate_reacquires(self):
        reader=CircularReader(ROOT/'src/assets')
        for width,height,center in ((1920,1072,None),(800,599,(550,350)),(1280,720,(700,380))):
            reading=reader.read(frame(width,height,False,center))
            self.assertIsNotNone(reading,(width,height))
            self.assertEqual(reading.mouse_button,'left')
            expected=center or (width*.772,height*.537)
            self.assertLess(abs(reading.center[0]-expected[0]),10)

    def test_green_map_and_detached_arrow_do_not_issue_commands(self):
        reader=CircularReader(ROOT/'src/assets')
        for color in ((20,220,50),(24,100,150),(0,0,0)):
            image=np.full((599,800,3),color,dtype=np.uint8)
            cv2.putText(image,'^^',(590,140),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)
            self.assertIsNone(reader.read(image))

    def test_button_is_latched_only_while_ui_is_present(self):
        command=CircularCommand()
        reading=CircularReading((1,1),1,1.,mouse_button='right')
        self.assertEqual(command.step(reading,1),'right')
        reading.mouse_button=None
        self.assertEqual(command.step(reading,1.5),'right')
        self.assertEqual(command.step(None,1.6),'right')
        self.assertIsNone(command.step(None,1.7))
        self.assertIsNone(command.step(reading,2))
        reading.mouse_button='left'
        self.assertEqual(command.step(reading,2.1),'left')
        reading.complete=True
        self.assertIsNone(command.step(reading,2.2))


if __name__=='__main__':unittest.main()
