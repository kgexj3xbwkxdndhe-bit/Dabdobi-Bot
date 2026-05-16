import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "mod_config.json"
        self.load_config()

    # تحميل إعدادات روم السجلات
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"log_channel_id": None}
            self.save_config()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    # دالة فرعية لإرسال السجلات تلقائياً
    async def send_log(self, action_name, target: discord.Member, moderator: discord.Member, reason):
        channel_id = self.config.get("log_channel_id")
        if not channel_id:
            return # إذا لم يتم تحديد روم بعد، لن يفعل شيئاً
        
        channel = self.bot.get_channel(int(channel_id))
        if channel:
            # تصميم رسالة السجل بشكل احترافي (Embed)
            embed = discord.Embed(title=f"📝 سجل إدارة جديد | {action_name}", color=discord.Color.orange())
            embed.add_field(name="الـمُستهدف:", value=f"{target.mention} ({target.id})", inline=False)
            embed.add_field(name="المسؤول:", value=f"{moderator.mention}", inline=False)
            embed.add_field(name="السبب:", value=f"{reason if reason else 'لا يوجد سبب محدد'}", inline=False)
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.set_footer(text=f"التوقيت تلقائي عبر دبدوبي")
            await channel.send(embed=embed)

    # 1. أمر سلاش لتحديد روم السجلات تلقائياً
    @app_commands.command(name="set_log", description="تحديد روم إرسال سجلات الإدارة تلقائياً")
    @app_commands.describe(الروم="اختر الروم المراد إرسال السجلات إليه")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log(self, interaction: discord.Interaction, الروم: discord.TextChannel):
        self.config["log_channel_id"] = الروم.id
        self.save_config()
        await interaction.response.send_message(f"✅ تم تحديد {الروم.mention} كروم رسمي لتسجيل أعمال الإدارة بنجاح!", ephemeral=True)

    # 2. أمر الطرد العادي (مربوط بالسجلات تلقائياً)
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f'✅ تم طرد {member.display_name} بنجاح.')
            # إرسال للسجلات تلقائياً
            await self.send_log("طرد (Kick)", member, ctx.author, reason)
        except Exception as e:
            await ctx.send(f'❌ فشل الطرد: {e}')

    # 3. أمر الحظر العادي (مربوط بالسجلات تلقائياً)
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f'🚫 تم حظر {member.display_name} نهائياً.')
            # إرسال للسجلات تلقائياً
            await self.send_log("حظر (Ban)", member, ctx.author, reason)
        except Exception as e:
            await ctx.send(f'❌ فشل الحظر: {e}')

    # 4. أمر التحذير (مربوط بالسجلات تلقائياً)
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        embed = discord.Embed(title="⚠️ تحذير جديد", description=f"العضو: {member.mention}\nالسبب: {reason}\nبواسطة: {ctx.author.mention}", color=0xff0000)
        await ctx.send(content=member.mention, embed=embed)
        # إرسال للسجلات تلقائياً
        await self.send_log("تحذير (Warn)", member, ctx.author, reason)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
