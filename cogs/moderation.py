import discord
from discord import app_commands
from discord.ext import commands

class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_warnings = {}  # قاعدة بيانات مؤقتة للتحذيرات

    # ----------------- أمر الباند (/ban) -----------------
    @app_commands.command(name="ban", description="حظر عضو من السيرفر (باند)")
    @app_commands.describe(member="العضو المراد حظره", reason="السبب")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ لا يمكنك حظر عضو رتبته أعلى منك أو مساوية لك!", ephemeral=True)
            return
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"✈️ تم بنجاح حظر العضو {member.mention}\n**السبب:** {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ رتبة البوت أقل من رتبة هذا الشخص.", ephemeral=True)

    # ----------------- أمر الطرد (/kick) -----------------
    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @app_commands.describe(member="العضو المراد طرده", reason="السبب")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ لا يمكنك طرد عضو رتبته أعلى منك أو مساوية لك!", ephemeral=True)
            return
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"🚪 تم بنجاح طرد العضو {member.mention}\n**السبب:** {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ رتبة البوت أقل من رتبة هذا الشخص.", ephemeral=True)

    # ----------------- أمر التحذير (/warn) -----------------
    @app_commands.command(name="warn", description="توجيه تحذير لعضو")
    @app_commands.describe(member="العضو المراد تحذيره", reason="سبب التحذير")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if member.bot:
            await interaction.response.send_message("❌ لا يمكنك تحذير البوتات!", ephemeral=True)
            return

        if member.id not in self.user_warnings:
            self.user_warnings[member.id] = []
        
        self.user_warnings[member.id].append(reason)
        total_warns = len(self.user_warnings[member.id])

        await interaction.response.send_message(f"⚠️ تم تحذير {member.mention}\n**السبب:** {reason}\n**عدد تحذيراته الحالية:** {total_warns}")

        if total_warns >= 3:
            try:
                await member.kick(reason="تجاوز الحد الأقصى من التحذيرات")
                await interaction.channel.send(f"🚨 تم طرد {member.mention} تلقائياً بسبب وصوله إلى 3 تحذيرات!")
                self.user_warnings[member.id] = []
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Moderator(bot))
    
