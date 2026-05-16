import discord
from discord import app_commands
from discord.ext import commands

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # قاعدة بيانات مؤقتة للردود التلقائية والتحذيرات
        self.auto_responses = {}
        self.user_warnings = {}
        self.MAX_RESPONSES = 5  # الحد الأقصى للردود التلقائية

    # ----------------- 1. أمر إضافة رد تلقائي -----------------
    @app_commands.command(name="add_say", description="إضافة رد تلقائي جديد")
    @app_commands.describe(trigger="الكلمة التي يكتبها المستخدم (مثال: hi)", response="رد البوت عليها (مثال: هلا فيك)")
    async def add_say(self, interaction: discord.Interaction, trigger: str, response: str):
        if len(self.auto_responses) >= self.MAX_RESPONSES:
            await interaction.response.send_message(f"❌ عذراً، لقد وصلت للحد الأقصى من الردود ({self.MAX_RESPONSES})! امسح أحدها أولاً.", ephemeral=True)
            return

        for i in range(1, self.MAX_RESPONSES + 1):
            slot_name = f"option_{i}"
            if slot_name not in self.auto_responses:
                self.auto_responses[slot_name] = {
                    "trigger": trigger.lower().strip(),
                    "response": response
                }
                await interaction.response.send_message(f"✅ تم إضافة الرد بنجاح في **{slot_name}**!\nإذا أحد قال: `{trigger}` سأرد بـ: `{response}`", ephemeral=True)
                return

    # ----------------- 2. أمر منع (حذف) رد تلقائي -----------------
    @app_commands.command(name="remove_say", description="منع وحذف رد تلقائي معين")
    @app_commands.describe(option="اختر رقم الخيار الذي تريد حذفه من القائمة")
    @app_commands.choices(option=[
        app_commands.Choice(name="Option 1", value="option_1"),
        app_commands.Choice(name="Option 2", value="option_2"),
        app_commands.Choice(name="Option 3", value="option_3"),
        app_commands.Choice(name="Option 4", value="option_4"),
        app_commands.Choice(name="Option 5", value="option_5"),
    ])
    async def remove_say(self, interaction: discord.Interaction, option: app_commands.Choice[str]):
        slot = option.value
        if slot in self.auto_responses:
            old_trigger = self.auto_responses[slot]['trigger']
            del self.auto_responses[slot]
            await interaction.response.send_message(f"🛑 تم منع وحذف الرد الخاص بـ **{option.name}** (الكلمة الممنوعة: `{old_trigger}`).", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ **{option.name}** فارغ بالفعل ولا يحتوي على أي رد لمنعه.", ephemeral=True)

    # ----------------- 3. الاستماع للرسائل (الرد التلقائي) -----------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        user_text = message.content.lower().strip()
        for slot, data in self.auto_responses.items():
            if user_text == data["trigger"]:
                await message.channel.send(data["response"])
                break

    # ----------------- 4. أمر الباند (/ban) -----------------
    @app_commands.command(name="ban", description="حظر عضو من السيرفر (باند)")
    @app_commands.describe(member="العضو المراد حظره", reason="السبب (اختياري)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ لا يمكنك حظر عضو رتبته أعلى منك أو مساوية لك!", ephemeral=True)
            return
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"✈️ تم بنجاح حظر العضو {member.mention}\n**السبب:** {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ رتبة البوت أقل من رتبة هذا الشخص في السيرفر.", ephemeral=True)

    # ----------------- 5. أمر الطرد (/kick) -----------------
    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @app_commands.describe(member="العضو المراد طرده", reason="السبب (اختياري)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ لا يمكنك طرد عضو رتبته أعلى منك أو مساوية لك!", ephemeral=True)
            return
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"🚪 تم بنجاح طرد العضو {member.mention}\n**السبب:** {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ رتبة البوت أقل من رتبة هذا الشخص في السيرفر.", ephemeral=True)

    # ----------------- 6. أمر التحذير (/warn) -----------------
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
                await member.kick(reason="تجاوز الحد الأقصى من التحذيرات (3 تحذيرات)")
                await interaction.channel.send(f"🚨 تم طرد {member.mention} تلقائياً بسبب وصوله إلى
                
