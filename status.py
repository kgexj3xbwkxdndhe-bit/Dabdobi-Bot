import discord
from discord.ext import commands
from discord import app_commands
import time

class SystemCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="فحص حالة النظام والأوامر للتأكد من عملها")
    @app_commands.checks.has_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction):
        # 1. قياس سرعة استجابة البوت (Ping)
        ping = round(self.bot.latency * 1000)
        
        # 2. فحص الـ Cogs (الملفات الفرعية) لمعرفة الشغال والمعطل
        # الأكواد تبحث عن اسم الـ Class الذي وضعناه في كل ملف
        welcome_status = "🟢 شغال تمام" if "Welcome" in self.bot.cogs else "🔴 معطل أو فيه خطأ"
        moderation_status = "🟢 شغال تمام" if "Moderation" in self.bot.cogs else "🔴 معطل أو فيه خطأ"
        actions_status = "🟢 شغال تمام" if "Actions" in self.bot.cogs else "🔴 معطل أو فيه خطأ"
        
        # 3. فحص صلاحيات البوت الأساسية في السيرفر
        bot_member = interaction.guild.me
        can_ban = "✅ متوفرة" if bot_member.guild_permissions.ban_members else "❌ مفقودة (حمل رتبة البوت)"
        can_kick = "✅ متوفرة" if bot_member.guild_permissions.kick_members else "❌ مفقودة (حمل رتبة البوت)"
        can_manage_messages = "✅ متوفرة" if bot_member.guild_permissions.manage_messages else "❌ مفقودة"

        # 4. بناء تقرير النظم الاحترافي (Embed)
        embed = discord.Embed(
            title="🖥️ لوحة فحص سلامة نظام دبدوبي", 
            description="تقرير فوري يوضح حالة الأوامر والملفات البرمجية داخل الاستضافة:", 
            color=discord.Color.blue()
        )
        
        # قسم الملفات والأوامر
        embed.add_field(name="📦 نظام الترحيب والـ GIF (welcome.py):", value=welcome_status, inline=False)
        embed.add_field(name="🛡️ نظام الإدارة والسجلات (moderation.py):", value=moderation_status, inline=False)
        embed.add_field(name="📬 نظام الأوامر والرسائل (actions.py):", value=actions_status, inline=False)
        
        # قسم الأداء والصلاحيات
        embed.add_field(name="⚡ سرعة استجابة البوت (Ping):", value=f"{ping} ميلي ثانية (ms)", inline=True)
        embed.add_field(name="🤖 حالة الاتصال بديسكورد:", value="🟢 متصل 24س", inline=True)
        
        # قسم فحص صلاحيات الإدارة الهامة
        embed.add_field(
            name="📋 فحص صلاحيات البوت بالسيرفر:", 
            value=f"الحظر (Ban): {can_ban}\nالطرد (Kick): {can_kick}\nإدارة الرسائل (Say/Warn): {can_manage_messages}", 
            inline=False
        )
        
        embed.set_footer(text=f"طلب الفحص بواسطة: {interaction.user.display_name}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # إرسال التقرير للمشرف
        await interaction.response.send_message(embed=embed)

    # التعامل مع أخطاء الصلاحيات للأمر
    @status.error
    async def status_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ هذا الأمر مخصص لإدارة وسيرفر دبدوبي فقط (تحتاج صلاحية Administrator).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SystemCheck(bot))
