import discord
from discord import app_commands
from discord.ext import commands

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_responses = {}
        self.MAX_RESPONSES = 5  # الحد الأقصى للردود

    # ----------------- أمر إضافة رد تلقائي -----------------
    @app_commands.command(name="add_say", description="إضافة رد تلقائي جديد للكلمات")
    @app_commands.describe(trigger="الكلمة التي يبحث عنها البوت في الجملة", response="رد البوت عليها")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def add_say(self, interaction: discord.Interaction, trigger: str, response: str):
        if len(self.auto_responses) >= self.MAX_RESPONSES:
            await interaction.response.send_message(f"❌ وصلت للحد الأقصى من الردود ({self.MAX_RESPONSES})! امسح أحدها أولاً.", ephemeral=True)
            return

        for i in range(1, self.MAX_RESPONSES + 1):
            slot_name = f"option_{i}"
            if slot_name not in self.auto_responses:
                self.auto_responses[slot_name] = {
                    "trigger": trigger.lower().strip(),
                    "response": response
                }
                await interaction.response.send_message(f"✅ تم إضافة الرد بنجاح!\nإذا احتوت الجملة على: `{trigger}` سأرد بـ: `{response}`", ephemeral=True)
                return

    # ----------------- أمر حذف رد تلقائي -----------------
    @app_commands.command(name="remove_say", description="منع وحذف رد تلقائي معين")
    @app_commands.describe(option="اختر رقم الخيار لحذفه")
    @app_commands.choices(option=[
        app_commands.Choice(name="Option 1", value="option_1"),
        app_commands.Choice(name="Option 2", value="option_2"),
        app_commands.Choice(name="Option 3", value="option_3"),
        app_commands.Choice(name="Option 4", value="option_4"),
        app_commands.Choice(name="Option 5", value="option_5"),
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def remove_say(self, interaction: discord.Interaction, option: app_commands.Choice[str]):
        slot = option.value
        if slot in self.auto_responses:
            old_trigger = self.auto_responses[slot]['trigger']
            del self.auto_responses[slot]
            await interaction.response.send_message(f"🛑 تم حذف الرد الخاص بـ **{option.name}** (الكلمة: `{old_trigger}`).", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ الخيار فارغ بالفعل.", ephemeral=True)

    # ----------------- الاستماع للرسائل (البحث الذكي) -----------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        user_text = message.content.lower().strip()
        
        for slot, data in self.auto_responses.items():
            if data["trigger"] in user_text:
                await message.channel.send(data["response"])
                break

async def setup(bot):
    await bot.add_cog(Actions(bot))
