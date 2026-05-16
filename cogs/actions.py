import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة فرعية للإرسال في الخلفية لحماية البوت من التجمد (تخدم أمر say المطور)
    async def run_say_loop(self, channel, webhook, طريقة_الإرسال, الرسالة, عدد_التكرار):
        for _ in range(عدد_التكرار):
            try:
                if طريقة_الإرسال == "bot":
                    await channel.send(الرسالة)
                elif طريقة_الإرسال == "webhook":
                    await webhook.send(content=الرسالة, username="دبدوبي الخارق", avatar_url=self.bot.user.display_avatar.url)
                
                # الفاصل الزمني (5 ثوانٍ) لمنع حظر ديسكورد وبدون ضغط
                await asyncio.sleep(5.0)
            except Exception as e:
                print(f"حدث خطأ أثناء الإرسال المكرر: {e}")
                break

    # 1. أمر /say المطور والضخم (البوت أو Webhook + التكرار حتى 999)
    @app_commands.command(name="say", description="إرسال رسالة مكررة في الخلفية عبر البوت أو Webhook مخصص")
    @app_commands.describe(
        الرسالة="اكتب النص الذي تريد من البوت إرساله",
        طريقة_الإرسال="اختر هل ترسل الرسالة باسم البوت أو عبر Webhook مخصص والسيرفر",
        عدد_التكرار="كم مرة تريد تكرار الرسالة؟ (الحد الأقصى 999 مرة)"
    )
    @app_commands.choices(طريقة_الإرسال=[
        app_commands.Choice(name="🤖 إرسال باسم البوت العادي", value="bot"),
        app_commands.Choice(name="🌐 إرسال عبر الـ Webhook مخصص", value="webhook")
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, الرسالة: str, طريقة_الإرسال: str, عدد_التكرار: int = 1):
        if عدد_التكرار < 1:
            عدد_التكرار = 1
        elif عدد_التكرار > 99999:
            await interaction.response.send_message("⚠️ الحد الأقصى المسموح به حالياً في الكود هو 99999 مرة فقط!", ephemeral=True)
            return

        await interaction.response.send_message(f"🚀 تم إطلاق المهمة بنجاح! سيتم إرسال الرسالة {عدد_التكرار} مرة كل 5 ثوانٍ في الخلفية بدون ضغط.", ephemeral=True)

        webhook = None
        if طريقة_الإرسال == "webhook":
            channel = interaction.channel
            webhooks = await channel.webhooks()
            webhook = discord.utils.get(webhooks, name="Dabdobi Webhook")
            if not webhook:
                webhook = await channel.create_webhook(name="Dabdobi Webhook", avatar=await self.bot.user.avatar.read())

        asyncio.create_task(self.run_say_loop(interaction.channel, webhook, طريقة_الإرسال, الرسالة, عدد_التكرار))


    # 2. أمر /say_embed لإرسال الرسائل المنسقة والملونة
    @app_commands.command(name="say_embed", description="إرسال رسالة منسقة داخل إطار ملون (Embed)")
    @app_commands.describe(
        العنوان="عنوان الرسالة المنسقة",
        الوصف="محتوى الرسالة المنسقة التفصيلي",
        اللون="اختر لون الإطار الجانبي للرسالة"
    )
    @app_commands.choices(اللون=[
        app_commands.Choice(name="🔴 أحمر", value="red"),
        app_commands.Choice(name="🔵 أزرق", value="blue"),
        app_commands.Choice(name="🟢 أخضر", value="green"),
        app_commands.Choice(name="🟡 أصفر", value="yellow")
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say_embed(self, interaction: discord.Interaction, العنوان: str, الوصف: str, اللون: str = "blue"):
        # تحويل اختيار اللون إلى لغة ديسكورد الرسمية
        color_map = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "yellow": discord.Color.yellow()
        }
        
        # بناء الـ Embed هندسياً
        embed = discord.Embed(
            title=العنوان,
            description=الوصف,
            color=color_map.get(اللون, discord.Color.blue())
        )
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        # إرسال الـ Embed في الروم
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال الـ Embed بنجاح!", ephemeral=True)


    # 3. أمر /say_dm لإرسال رسالة مباشرة لعضو في الخاص باسم البوت
    @app_commands.command(name="say_dm", description="إرسال رسالة خاصة إلى عضو معين عبر البوت")
    @app_commands.describe(
        العضو="اختار الشخص الذي تريد إرسال الرسالة له",
        الرسالة="اكتب نص الرسالة الخاصة"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say_dm(self, interaction: discord.Interaction, العضو: discord.User, الرسالة: str):
        try:
            # فتح الخاص الخاص بالعضو وإرسال الرسالة له
            await العضو.send(f"📬 **لديك رسالة جديدة من إدارة السيرفر:**\n\n{الرسالة}")
            await interaction.response.send_message(f"✅ تم إرسال الرسالة الخاصة إلى {العضو.mention} بنجاح!", ephemeral=True)
        except discord.Forbidden:
            # إذا كان العضو مغلق خاص حسابه
            await interaction.response.send_message(f"❌ لم أتمكن من إرسال الرسالة إلى {العضو.mention} لأن الخاص لديه مغلق!", ephemeral=True)


    # 4. ميزة الرد التلقائي الذكي على كلمة !hi
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if "!hi" in message.content.lower():
            await message.channel.send('أهلاً بك! دبدوبي في الخدمة ومستعد للأوامر المتقدمة. 🐾')


    # التعامل الموحد مع أخطاء صلاحيات الأوامر في هذا الملف
    @say.error
    @say_embed.error
    @say_dm.error
    async def actions_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ تحتاج إلى صلاحية `إدارة الرسائل` لاستخدام هذه الأوامر الإدارية.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Actions(bot))
    
