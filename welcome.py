import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageSequence
import io
import requests
import json
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "welcome_config.json"
        self.load_config()

    # دالة لتحميل الإعدادات من ملف JSON
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            # إعدادات افتراضية إذا كان الملف غير موجود
            self.config = {
                "img1": "https://cdn.discordapp.com/attachments/1491146217260847124/1504880901501489243/c32907ac10dd46d2b94de7f37df71cfd.gif",
                "img2": "https://placehold.co/1280x720?text=Image+2+Not+Set",
                "active_slot": "1"
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    # 1. أمر السلاش لضبط رابط الصورة
    @app_commands.command(name="welcome_set", description="ضبط رابط صورة الترحيب للخانة 1 أو 2")
    @app_commands.describe(الخانة="اختر الخانة التي تريد حفظ الرابط فيها", الرابط="ضع رابط الصورة أو الـ GIF هنا")
    @app_commands.choices(الخانة=[
        app_commands.Choice(name="الصورة رقم 1", value="img1"),
        app_commands.Choice(name="الصورة رقم 2", value="img2")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_set(self, interaction: discord.Interaction, الخانة: str, الرابط: str):
        self.config[الخانة] = الرابط
        self.save_config()
        await interaction.response.send_message(f"✅ تم حفظ الرابط بنجاح في **{الخانة}**.", ephemeral=True)

    # 2. أمر السلاش لاختيار أي صورة سيستخدمها البوت حالياً
    @app_commands.command(name="welcome_use", description="اختيار أي خانة ترحيب سيتم تفعيلها الآن")
    @app_commands.describe(الخانة="اختر الخانة المراد تفعيلها")
    @app_commands.choices(الخانة=[
        app_commands.Choice(name="استخدام الصورة 1", value="1"),
        app_commands.Choice(name="استخدام الصورة 2", value="2")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_use(self, interaction: discord.Interaction, الخانة: str):
        self.config["active_slot"] = الخانة
        self.save_config()
        await interaction.response.send_message(f"🚀 البوت الآن سيستخدم **الصورة رقم {الخانة}** عند دخول الأعضاء الجدد.", ephemeral=True)

    # 3. حدث الترحيب (تعديل لجعل الرابط متغيراً)
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(1491147425833029672) # ايدي الروم
        if not channel: return

        # تحديد الرابط بناءً على الاختيار الحالي
        slot = self.config["active_slot"]
        BG_URL = self.config[f"img{slot}"]
        OVERLAY_URL = "https://cdn.discordapp.com/attachments/1491146217260847124/1504880891795734690/b0e6c5cb36d34e3990597a4da83232b5.gif"

        try:
            avatar_data = requests.get(member.display_avatar.url).content
            avatar_img = Image.open(io.BytesIO(avatar_data)).convert("RGBA").resize((200, 200))
            mask = Image.new("L", (200, 200), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 200, 200), fill=255)
            
            bg_data = requests.get(BG_URL).content
            bg_gif = Image.open(io.BytesIO(bg_data))
            overlay_gif = Image.open(io.BytesIO(requests.get(OVERLAY_URL).content))
            
            frames = []
            overlay_iter = ImageSequence.Iterator(overlay_gif)

            for frame in ImageSequence.Iterator(bg_gif):
                base = frame.convert("RGBA")
                base.paste(avatar_img, (400, 150), mask)
                try:
                    overlay_frame = next(overlay_iter).convert("RGBA")
                    # تنظيف الخلفية السوداء
                    datas = overlay_frame.getdata()
                    newData = [(0,0,0,0) if d[0]<30 and d[1]<30 and d[2]<30 else d for d in datas]
                    overlay_frame.putdata(newData)
                    base.alpha_composite(overlay_frame.resize(base.size))
                except StopIteration:
                    overlay_iter = ImageSequence.Iterator(overlay_gif)
                frames.append(base)

            output = io.BytesIO()
            frames[0].save(output, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=bg_gif.info.get('duration', 100))
            output.seek(0)
            await channel.send(f"مرحباً بك {member.mention}! تم استخدام القالب رقم {slot}", file=discord.File(fp=output, filename="welcome.gif"))
        except Exception as e:
            print(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
