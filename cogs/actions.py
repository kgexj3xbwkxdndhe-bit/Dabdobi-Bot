import discord
from discord import app_commands
from discord.ext import commands

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        
    async def setup_hook(self):
        # تضمن مزامنة الأوامر مع السيرفر
        await self.tree.sync()

bot = MyBot()

# قاعدة بيانات مؤقتة لتخزين الردود (في كود الإنتاج يفضل استخدام SQLite أو JSON)
# الهيكل سيكون: { "option_1": {"trigger": "hi", "response": "هلا فيك"} }
auto_responses = {}
MAX_RESPONSES = 5 # حد أقصى للردود لتجنب الفوضى

# ----------------- 1. أمر إضافة رد تلقائي -----------------
@bot.tree.command(name="add_say", description="إضافة رد تلقائي جديد")
@app_commands.describe(
    trigger="الكلمة التي يكتبها المستخدم (مثال: hi)",
    response="رد البوت عليها (مثال: هلا فيك)"
)
async def add_say(interaction: discord.Interaction, trigger: str, response: str):
    # التحقق من عدم تجاوز الحد الأقصى
    if len(auto_responses) >= MAX_RESPONSES:
        await interaction.response.send_message(f"❌ عذراً، لقد وصلت للحد الأقصى من الردود ({MAX_RESPONSES})! امسح أحدها أولاً.", ephemeral=True)
        return

    # البحث عن أول اسم خيار متاح (Option 1, Option 2...)
    for i in range(1, MAX_RESPONSES + 1):
        slot_name = f"option_{i}"
        if slot_name not in auto_responses:
            auto_responses[slot_name] = {
                "trigger": trigger.lower().strip(),
                "response": response
            }
            await interaction.response.send_message(f"✅ تم إضافة الرد بنجاح في **{slot_name}**!\nإذا أحد قال: `{trigger}` سأرد بـ: `{response}`", ephemeral=True)
            return

# ----------------- 2. أمر منع (حذف) رد تلقائي -----------------
@bot.tree.command(name="remove_say", description="منع وحذف رد تلقائي معين")
@app_commands.describe(option="اختر رقم الخيار الذي تريد حذفه من القائمة")
# استخدام choices لإظهار القائمة بشكل احترافي للمستخدم (Option 1, Option 2...)
@app_commands.choices(option=[
    app_commands.Choice(name="Option 1", value="option_1"),
    app_commands.Choice(name="Option 2", value="option_2"),
    app_commands.Choice(name="Option 3", value="option_3"),
    app_commands.Choice(name="Option 4", value="option_4"),
    app_commands.Choice(name="Option 5", value="option_5"),
])
async def remove_say(interaction: discord.Interaction, option: app_commands.Choice[str]):
    slot = option.value
    
    if slot in auto_responses:
        old_trigger = auto_responses[slot]['trigger']
        del auto_responses[slot] # حذف الرد من قاعدة البيانات
        await interaction.response.send_message(f"🛑 تم منع وحذف الرد الخاص بـ **{option.name}** (الكلمة الممنوعة: `{old_trigger}`).", ephemeral=True)
    else:
        await interaction.response.send_message(f"ℹ️ **{option.name}** فارغ بالفعل ولا يحتوي على أي رد لمنعه.", ephemeral=True)

# ----------------- 3. الاستماع للرسائل لتفعيل الردود -----------------
@bot.event
async def on_message(message: message):
    # تجنب رد البوت على نفسه
    if message.author == bot.user:
        return

    # تنظيف النص المرسل (تحويله لسمول وإزالة المسافات الزائدة)
    user_text = message.content.lower().strip()

    # الفحص إذا كانت الكلمة موجودة في قاعدة البيانات
    for slot, data in auto_responses.items():
        if user_text == data["trigger"]:
            await message.channel.send(data["response"])
            break # التوقف بعد إيجاد أول تطابق

    await bot.process_commands(message)

# ضع التوكن الخاص ببوت Dabdobi هنا
bot.run("YOUR_BOT_TOKEN")
