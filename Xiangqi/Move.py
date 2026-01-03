from Xiangqi import common 
from common import piece_map_etc
from Xiangqi.FEN import FEN
import re

class Move(FEN):

    def __init__(self,fen,moves):
        super().__init__(fen)
        self.moves = moves
        self.movesCHN=[]
        self.piece_counts = {}
        self.piece_moves = {}
        self.moves_etc()

    # UCI moves

    @staticmethod
    def _parse_move(move):
        # 10 abcdefghi (0,0)
        # 9
        # ...
        # 2
        # 1  abcdefghi

        if not(len(move) in (4,5,6)):
            raise ValueError("length of move must be 4!")

        m = re.fullmatch(r"([a-i])(10|[1-9])([a-i])(10|[1-9])", move)
        if not m:
            raise ValueError("Regular Expressions!")

        sx = ord(m.group(1)) - ord("a")
        sy = 10 - int(m.group(2))
        tx = ord(m.group(3)) - ord("a")
        ty = 10 - int(m.group(4))

        return sx,sy,tx,ty


    def _apply_move(self, sx,sy,tx,ty):

        piece = self.board[sy][sx]

        if piece == ".":
            return f'**{self.turn_red}**no piece**'

        is_red = piece.isupper()
        name = piece_map_etc[piece]

        start_file = numerals_etc(9-sx) if is_red else str(sx+1)
        end_file = numerals_etc(9-tx)if is_red else str(tx+1)

        dx = tx - sx
        dy = ty - sy

        notation = ""

        if piece.upper() in ["N","B","A"]:  # Knight, Elephant, Advisor
            # Always show starting file + direction + target file
            direction = "进" if (dy < 0 and is_red) or (dy > 0 and not is_red) else "退"
            notation = f"{name}{start_file}{direction}{end_file}"
        else:  # Rook, Cannon, Pawn, King
            if sx == tx:  # vertical
                if is_red:
                    direction = "进" if ty < sy else "退"
                else:
                    direction = "进" if ty > sy else "退"
                steps = abs(ty - sy)
                if is_red: steps = numerals_etc(steps)
                notation = f"{name}{start_file}{direction}{steps}"
            elif sy == ty:  # horizontal
                notation = f"{name}{start_file}平{end_file}"
            else:  # uncommon diagonal (King in palace)
                if is_red:
                    direction = "进" if ty < sy else "退"
                else:
                    direction = "进" if ty > sy else "退"
                notation = f"{name}{start_file}{direction}{end_file}"

        # Update board
        self.board[sy][sx] = "."
        self.board[ty][tx] = piece

        self._from_matrix()
        self.fens.append(self.fen)

        # Alternate side
        self.turn_red = not self.turn_red

        return notation


    def moves_etc(self):

        self.movesCHN = []

        for mv in self.moves:
            try:
                sx,sy,tx,ty = self._parse_move(mv)
                notation = self._apply_move(sx,sy,tx,ty)
                self.movesCHN.append(notation)

            except Exception as e:
                print(e)
                self.movesCHN.append('****')
                self.turn_red = not self.turn_red
                continue

    def animation(self):

        # .gif
        frames=[]
        for i, fen in enumerate(self.fens):
            img = FEN(fen).draw()
            frames.append(img)

        import glob

        # save as gif
        frames[0].save(
            "animation.gif",
            save_all=True,
            append_images=frames[1:],
            duration=2000,   # milliseconds per frame (0.5s)
            loop=0          # loop forever
        )

        moves = self.movesCHN

        # Audio
        from gtts import gTTS
        from moviepy.editor import AudioFileClip,VideoFileClip, concatenate_audioclips, CompositeAudioClip, AudioClip
        import numpy as np

        unique_moves = list(set(moves))

        voice_lib = {}
        for move in unique_moves:
            tts_file = f"{move}.mp3"
            tts = gTTS(text=move, lang='zh')
            tts.save(tts_file)
            voice_lib[move] = tts_file


        desired_duration = 2

        audio_clips = []

        for move in moves:
            tts_clip = AudioFileClip(voice_lib[move])

            if tts_clip.duration < desired_duration:
                remaining = desired_duration - tts_clip.duration
                silent_bg = AudioClip(lambda t: np.array([0.0]), duration=remaining)
                tts_clip = concatenate_audioclips([tts_clip, silent_bg]).set_duration(2)
            audio_clips.append(tts_clip)

        combined_audio = concatenate_audioclips(audio_clips)

        # combine audio and video

        clip = VideoFileClip("animation.gif")
        clip = clip.set_audio(combined_audio.set_start(0.3))
        clip.write_videofile("final_with_voice.mp4", codec="libx264", audio_codec="aac", fps=24)

        # subtitles
        
        filename="subtitles.srt"
        with open(filename, "w", encoding="utf-8-sig") as f:
            for i, text in enumerate(self.movesCHN):
                start_seconds = i * 2
                end_seconds = start_seconds + 2

                start_h = start_seconds // 3600
                start_m = (start_seconds % 3600) // 60
                start_s = start_seconds % 60

                end_h = end_seconds // 3600
                end_m = (end_seconds % 3600) // 60
                end_s = end_seconds % 60

                f.write(f"{i+1}\n")
                f.write(f"{start_h:02}:{start_m:02}:{start_s:02},000 --> {end_h:02}:{end_m:02}:{end_s:02},000\n")
                f.write(f"{text}\n\n")

        import os
        os.system("ffmpeg -y -i final_with_voice.mp4 -vf subtitles=subtitles.srt output.mp4")
        
