from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
import random

# ------主菜单------
cd = on_command(
    '菜单',
    aliases={'menu','帮助'},
    block=True,
    priority=10
)

@cd.handle()  
async def main(bot: Bot):
    data = f"🌟 {list(bot.config.nickname)[0]}\n📄 [指令菜单] \n\n🎮 /游戏 -> 游戏菜单\n🎉 /娱乐 -> 娱乐菜单\n🛠️ /工具 -> 工具菜单\n🔎 /状态 -> 查询状态\n\n📌 发送对应命令以触发功能！\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await cd.finish(data)

# 【游戏系统】
# ------游戏系统菜单------
yxxt = on_command(
    '游戏',
    block=True,
    priority=10
)

@yxxt.handle()  
async def main():
    data = "🎮 [游戏系统菜单]\n\n1️⃣ /人生重开\n2️⃣ /扫雷\n3️⃣ /猜单词\n4️⃣ /猜成语\n5️⃣ /国际棋类\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await yxxt.finish(data)

# ------人生重开菜单------
rsck = on_command(
    '人生重开',
    block=True,
    priority=10
)

@rsck.handle()  
async def main():
    data = "开始游戏：@我+/人生重开\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await rsck.finish(data)

# ------扫雷菜单------
slxt = on_command(
    '扫雷',
    block=True,
    priority=10
)

@slxt.handle()  
async def main():
    data = "开始游戏：@我+/扫雷(初级/中级/高级)\n挖开方块：/挖开+位置\n标记方块：/标记+位置\n添加人员：/添加人员+@某人\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await slxt.finish(data)

# ------猜成语菜单------
ccyxt = on_command(
    '猜成语',
    block=True,
    priority=10
)

@ccyxt.handle()  
async def main():
    data = "开始游戏：@我+猜成语\n游戏规则：\n你有十次的机会猜一个四字词语\n每次猜测后，汉字与拼音的颜色将会标识其与正确答案的区别\n青色 表示其出现在答案中且在正确的位置\n橙色 表示其出现在答案中但不在正确的位置\n当四个格子都为青色时，你便赢得了游戏！\n可发送“结束”结束游戏\n可发送“提示”查看提示\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await ccyxt.finish(data)

# ------猜单词菜单------
cdcxt = on_command(
    '猜单词',
    block=True,
    priority=10
)

@cdcxt.handle()  
async def main():
    data = "开始游戏：@我+/猜单词”\n游戏规则：\n绿色块代表此单词中有此字母且位置正确\n黄色块代表此单词中有此字母，但该字母所处位置不对\n灰色块代表此单词中没有此字母\n猜出单词或用光次数则游戏结束\n可发送“结束”结束游戏\n可发送“提示”查看提示\n高级玩法：\n可使用 -l / --length 指定单词长度，默认为 5\n可使用 -d / --dic 指定词典，默认为 CET4\n支持的词典：GRE、考研、GMAT、专四、TOEFL、SAT、专八、IELTS、CET4、CET6\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await cdcxt.finish(data)

# ------国际棋类菜单------
gjqlxt = on_command(
    '国际棋类',
    block=True,
    priority=10
)

@gjqlxt.handle()  # 国际棋类系统响应体
async def main():
    data = "棋类：五子棋、围棋（禁全同，暂时不支持点目）、黑白棋\n开始游戏：@我+/棋类”,一个群内同时只能有一个棋局\n发送“落子 字母+数字”下棋，如“落子 A1”\n游戏发起者默认为先手，可使用 --white 选项选择后手\n发送“结束下棋”结束当前棋局\n发送“查看棋局”显示当前棋局\n发送“悔棋”可以进行悔棋\n发送“跳过回合”可跳过当前回合（仅黑白棋支持）\n手动结束游戏或超时结束游戏时，可发送“重载xx棋局”继续下棋，如:重载围棋棋局\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await gjqlxt.finish(data)


# 【娱乐系统】
# ------娱乐系统菜单------
ylxt = on_command(
    '娱乐',
    block=True,
    priority=10
)

@ylxt.handle()  
async def main():
    data = "🎉 [娱乐系统菜单]\n\n1️⃣ /文本\n2️⃣ /图片\n3️⃣ /新闻\n4️⃣ /塔罗牌\n5️⃣ /今日老婆帮助\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await ylxt.finish(data)

# ------文本菜单------
wbl = on_command(
    '文本',
    block=True,
    priority=10
)

@wbl.handle()  
async def main():
    data = "📝 [文本菜单]\n\n✨/一言\n✨/整点骚话\n✨/毒鸡汤\n✨/伤感语录\n✨/土味情话\n✨/舔狗日记\n✨/网易云热评\n\n📌 [发病语录]\n/发病 + 发病对象(默认为主人)\n\n📌 [天天疯狂]\n疯狂星期[一|二|三|四|五|六|日|天]\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await wbl.finish(data)

# ------图片菜单------
tpxt = on_command(
    '图片',
    block=True,
    priority=10
)

@tpxt.handle()  
async def main():
    data = "🖼️ [图片菜单]\n\n📄 使用“/+关键词”返回对应图片！\n✨/鬼刀✨/灵梦✨/东方✨/丁真✨/猫娘✨/猫猫✨/miku✨/cosplay✨/jk✨/meme✨/龙图✨/赛马娘\n\n📌 [搜图插件]\n/搜图 + 分类\n当前分类：all,mp,pc,1080p,silver,furry,starry,setu,ws,pixiv\n\n📌 [SexPhoto API]\n/色图 + 数量 + 关键词 + 标签\n\n📌 [Lolicon API]\nsetu|色图|涩涩 + 数量 + 关键词\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await tpxt.finish(data)

# ------新闻菜单------
xwrbl = on_command(
    '新闻',
    block=True,
    priority=10
)

@xwrbl.handle()  
async def main():
    data = "📰 [新闻热榜]\n\n✨/60s -> 每日60秒新闻\n✨/历史 -> 历史上的今天\n✨/电影票房 -> 当前电影票房\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await xwrbl.finish(data)

# ------塔罗牌菜单------
tlp = on_command(
    '塔罗牌',
    block=True,
    priority=10
)

@tlp.handle()  
async def main():
    data = "💡 [ba塔罗牌]\n\n✨/ba塔罗牌\n✨/ba占卜\n✨/ba运势\n✨/ba塔罗牌解读\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await tlp.finish(data)

# 【工具系统】
# ------工具系统菜单------
gjxt = on_command(
    '工具',
    block=True,
    priority=10
)

@gjxt.handle()  
async def main():
    data = "🛠️ [工具菜单]\n\n1️⃣ /天气查询\n2️⃣ /消息撤回\n3️⃣ /淫语转换\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await gjxt.finish(data)

# ------天气查询菜单------
tqcx = on_command(
    '天气查询',
    block=True,
    priority=10
)

@tqcx.handle()  
async def main():
    data = "输入“/天气+省份名|城市名”\n如:“/天气深圳”\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await tqcx.finish(data)

# ------消息撤回菜单------
xxch = on_command(
    '消息撤回',
    block=True,
    priority=10
)

@xxch.handle()  
async def main():
    data = "对我的消息回复“/撤回”可帮我撤回不合适的言论喔\n\n📢 防封编码："
    data += str(random.randint(10000, 99999))
    await xxch.finish(data)

# ------淫语转换菜单------
yyzh = on_command(
    '淫语转换',
    block=True,
    priority=10
)

@yyzh.handle()  
async def main():
    data = "指令：“/淫语+要转换的句子+淫乱度（可选）”\n如：“/淫语 不能再这样下去了啊 80%”\nn📢 防封编码："
    data += str(random.randint(10000, 99999))
    await yyzh.finish(data)