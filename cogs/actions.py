import discord
from discord.ext import commands
from discord import app_commands # مكتبة أوامر السلاش المتطورة

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر السلاش /say مع الخيارات الذكية
    @app_commands.command(name="say", description="إرسال رسالة مخصصة (عام في الروم أو خاص لعضو معين)")
    @app_commands.describe(
        نوع_الرسالة="اختر هل تريد إرسال الرسالة في الروم الحالي (عام) أم في الخاص لعضو؟",
        الرسالة="اكتب النص الذي تريد من دبدوبي أن يرسله",
        العضو="اختر العضو (مطلوب فقط إذا اخترت إرسال الرسالة في الخاص)"
    )
    # تحديد الاختيارات المتاحة للمشرف
    @app_commands.choices(نوع_الرسالة=[
        app_commands.Choice(name="عام (في الروم الحالي)", value="public"),
        app_commands.Choice(name="خاص (إلى عضو معين)", value="private")
    ])
    @app_commands.checks.has_permissions(manage_messages=True) # صلاحية استخدام الأمر
    async def say(self, interaction: discord.Interaction, نوع_الرسالة: str, الرسالة: str, العضو: discord.Member = None):
        
        # 1. إذا اختار إرسال في العام (الروم الحالي)
        if نوع_الرسالة == "public":
            # الرد على الـ Interaction بشكل مخفي لكي لا يرى الأعضاء أنك استخدمت الأمر
            await interaction.response.send_message("جاري إرسال الرسالة في الروم...", ephemeral=True)
            # إرسال الرسالة في الروم
            await interaction.channel.send(الرسالة)

        # 2. إذا اختار إرسال في الخاص
        elif نوع_الرسالة == "private":
            # التأكد أولاً أنه اختار عضواً
            if العضو is None:
                await interaction.response.send_message("❌ خطأ: يجب عليك تحديد العضو الذي تريد الإرسال له في الخاص!", ephemeral=True)
                return
            
            try:
                # محاولة إرسال الرسالة في خاص العضو
                await interaction.response.send_message(f"جاري إرسال الرسالة إلى خاص {العضو.display_name}...", ephemeral=True)
                await العضو.send(f"📬 **وصلتك رسالة من إدارة السيرفر:**\n\n{الرسالة}")
            except discord.Forbidden:
                # إذا كان العضو مغلقاً للخاص (Direct Messages)
                await interaction.followup.send(f"❌ لم أتمكن من إرسال الرسالة لـ {العضو.mention} لأن حسابه مغلق للرسائل الخاصة.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ حدث خطأ غير متوقع: {e}", ephemeral=True)

    # التعامل مع أخطاء الصلاحيات
    @say.error
    async def say_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ ليس لديك صلاحية استخدام هذا الأمر (تحتاج صلاحية إدارة الرسائل).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Actions(bot))
