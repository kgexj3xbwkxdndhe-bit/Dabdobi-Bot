import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. أمر /say المطور مع الخيارات المتقدمة (البوت أو Webhook + التكرار)
    @app_commands.command(name="say", description="إرسال رسالة مكررة عبر البوت أو عبر Webhook مخصص")
    @app_commands.describe(
        الرسالة="اكتب النص الذي تريد من البوت إرساله",
        طريقة_الإرسال="اختر هل ترسل الرسالة باسم البوت أو عبر Webhook مخصص والسيرفر",
        عدد_التكرار="كم مرة تريد تكرار الرسالة؟ (الحد الأقصى 5 مرات)"
    )
    @app_commands.choices(طريقة_الإرسال=[
        app_commands.Choice(name="🤖 إرسال باسم البوت العادي", value="bot"),
        app_commands.Choice(name="🌐 إرسال عبر الـ Webhook مخصص", value="webhook")
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, الرسالة: str, طريقة_الإرسال: str, عدد_التكرار: int = 1):
        # للتأكد أن المستخدم لم يضع رقماً سالباً أو كبيراً جداً لحماية السيرفر من السبام العشوائي
        if عدد_التكرار < 1:
            عدد_التكرار = 1
        elif عدد_التكرار > 5:
            await interaction.response.send_message("⚠️ الحد الأقصى للتكرار هو 5 مرات فقط لحماية السيرفر!", ephemeral=True)
            return

        # الرد الأولي المخفي حتى لا يعطي ديسكورد خطأ انتهاء وقت الاستجابة
        await interaction.response.send_message("🔄 جاري معالجة وإرسال طلبك...", ephemeral=True)

        # تنفيذ الإرسال بناءً على اختيار المستخدم
        if طريقة_الإرسال == "bot":
            for _ in range(عدد_التكرار):
                await interaction.channel.send(الرسالة)
                await asyncio.sleep(0.5) # فاصل زمني بسيط لتجنب حظر ديسكورد للأوامر السريعة
                
        elif طريقة_الإرسال == "webhook":
            # البحث عن Webhook موجود في الروم الحالي أو إنشاء واحد جديد هندسياً
            channel = interaction.channel
            webhooks = await channel.webhooks()
            webhook = discord.utils.get(webhooks, name="Dabdobi Webhook")
            
            if not webhook:
                # إذا لم يجد ويب هوك قديم، يصنع واحد باسم دبدوبي وصورته الشخصية تلقائياً
                webhook = await channel.create_webhook(name="Dabdobi Webhook", avatar=await self.bot.user.avatar.read())

            for _ in range(عدد_التكرار):
                # هنا يتم الإرسال عبر الويب هوك، ويمكنك مستقبلاً تخصيص اسم وصورة مختلفة لو أردت!
                await webhook.send(content=الرسالة, username="دبدوبي الخارق", avatar_url=self.bot.user.display_avatar.url)
                await asyncio.sleep(0.5)

    # 2. ميزة الرد التلقائي الذكي على كلمة !hi التي أعدناها سابقاً
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if "!hi" in message.content.lower():
            await message.channel.send('أهلاً بك! دبدوبي في الخدمة ومستعد للأوامر المتقدمة. 🐾')

    # التعامل مع أخطاء صلاحيات الأمر
    @say.error
    async def say_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ تحتاج إلى صلاحية `إدارة الرسائل` لاستخدام هذا الأمر.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Actions(bot))
    
