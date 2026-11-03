# 钩子系统与章尾防软化指南

网文读者靠章尾决定要不要翻页、要不要付费。钩子要在写细纲时设计好，不能写完再补。

商业网文付费转化的底层心法只有一条：**给读者“饥饿感（Visceral Urgency）”，坚决不给“饱腹感（Aesthetic Satiety）”！**

机器可读的类型表在 `references/hook-types.json`，校验由 `cws check` 的 `hooks` 项完成。

---

## 一、 商业网文的底层铁律：为什么章尾会“偏软”？

很多作者在追求文笔去 AI 味、提升人设深度的过程中，容易犯一个致命错误：**把章尾写成“文学闭环”**。

* **文学饱腹感（弃读陷阱）**：
  章节完整解决了上一个矛盾，结尾男女主互相打趣一句金句（Button），或者女主脱了鞋上床休息，或者女主打开电脑开始做表格。读者心里觉得“这章写得真高级、真妥帖”——**然后心满意足地合上手机睡觉，次日留存归零**。
* **商业饥饿感（付费翻页）**：
  读者停留在最焦虑、最刺激、生理冲动最强的那一瞬间。不点开下一章，读者今晚睡不着觉。

> **核心原则**：
> 所谓的“呼吸感”、“日常相处”、“文风润色”、“金句交流”，**全部必须发生在章中（Mid-Chapter）**！
> **每一章的章尾（最后 100 词），必须毫不留情地切入高压与未决！**

---

## 二、 半拍截断原则（The Mid-Action / Interruption Cut）

这是防章尾软化最重要的操作心法：**绝对不准在动作平稳落地后收笔，必须在“动作执行到一半”或“突发打断”的那一瞬间硬性掐断！**

| 软钩（错误：动作落地/饱腹感） | 硬钩（正确：半拍截断/危机掐喉） | 解析 |
| :--- | :--- | :--- |
| *She took off her shoes and stepped into the shower.*（她脱了鞋走向浴室） | *She unbuckled the strap of her left shoe. Behind her, a heavy key scraped violently inside the master lock.*（鞋扣刚解开，身后主锁孔猛地传来钥匙声） | 动作刚开始就被突发危机打断，读者必须看门后是谁 |
| *Vivian sat down at her desk, opened the laptop, and started a new spreadsheet.*（她坐下开始做表格） | *She clicked the spreadsheet tab. Under 'Offshore Wire', the signature wasn’t Julian’s—it was her father’s from three years ago.*（表格一点开，爆出毁灭性秘密） | 拒绝过程交代，一瞬间引爆信息核弹 |
| *“I’ll take the files up,” Vivian said, and pressed the button for the 48th floor.*（我说我去送，按了48楼） | *The elevator doors parted on 48. Julian was pinning a weeping woman against the glass wall, a shredded contract at his feet.*（电梯门一开，撞破骇人现场） | 不要在“去送”收尾，直接把读者扔到风暴中心 |
| *Julian smiled faintly and turned back to his screen.*（男主笑了笑转回屏幕） | *Julian’s hand caught her jaw before she cleared the door. “You leave this room,” he murmured against her mouth, “and your father goes to federal custody by noon.”*（直接身体逼近+生死筹码下注） | 用绝对力量感和压迫感封死退路 |

---

## 三、 类型表与分级梯队

| 分级 | id | 名称 | 章尾是什么样 | 下章开头怎么接 |
|---|---|---|---|---|
| **Tier 1<br>高转化硬钩**<br>*(入V/推荐期/强力推荐)* | `danger` | 危险逼近 | 人身、安全或处境危机已到眼前，停在发生前一微秒 | 落下这一击，或展开极限格挡 |
| | `caught` | 撞破 | 被致命第三人当场撞破，或差半寸抓包 | 撞见者的反应与当事人的圆场 |
| | `reveal` | 秘密漏缝 | 核心秘密被当面揭开一角，不可抵赖 | 追问或紧急掩盖这一角 |
| | `desire` | 欲望悬停 | 亲密或爆发停在临界点，绝不准写进事后 | 接住这一秒的触碰，不跳到第二天早上 |
| | `reversal` | 认知颠覆 | 刚刚确立的事实瞬间被推翻 | 人物当场的震惊与应急反应 |
| **Tier 2<br>推进型中钩**<br>*(日常连载交替推进)* | `message` | 突发消息 | 电话、短信、急电彻底颠覆当前局势 | 读完后的第一个应激动作 |
| | `deadline` | 绝境期限 | 死亡倒计时、筹钱最后期限压到眼前 | 人物开始争分夺秒抢时间 |
| | `showdown` | 清算在即 | 打脸、谈判、对质现场已经约死，不可逃避 | 直接进入对质现场第一句话 |
| | `decision` | 两难绝境 | 必须马上做二选一，两边都要流血付出代价 | 给出被逼到绝路的选择 |
| | `arrival` | 来人 | 不该出现的人物突然敲门或推门而入 | 来人开口的第一句话或肢体动作 |
| **Tier 3<br>软钩**<br>*(高弃读风险)* | `question` | 异常疑问 | 发现说不通的细节，提出新疑点 | 人物开始查，或故意不查 |
| | `button` | 金句收束 | 一句对白让关系换挡；**连载付费书慎用，禁止用于付费点！** | 顺着这句话的余波走 |

---

## 四、 强度标准与平台底线

| 强度 | 含义 | 连载 App（Dreame/AlphaNovel/番茄） | Kindle KU / 纸书长篇 |
|---|---|---|---|
| **1** | 轻：俏皮收束或小疑问 | ❌ **平台禁止**（易流失读者） | 过渡章可用 |
| **2** | 小：有一个明确的小问题，下章开头能解 | ⚠️ **仅限偶尔单章点缀，禁连续使用** | 日常章节标准 |
| **3** | 中：局面变了，出现新变量/新危机 | ✅ **连载网文及格线** | 推进章 |
| **4** | 强：关系、秘密、身体或安全实质受威胁 | 🔥 **付费前置章、推荐位期间标准** | 单元末 |
| **5** | 核弹：推翻全书既定事实、生死悬殊 | 💣 **入V卡点章、大高潮与卷末** | 全书最高潮 |

---

## 五、 细纲字段规范

```json
{
  "chapter": 7,
  "hook": {
    "type": "reveal",
    "strength": 4,
    "text": "保险箱里放着她三年前丢的带血护照",
    "keywords": ["passport", "blood"]
  },
  "catch": {
    "mode": "direct",
    "keywords": ["safe", "Julian"],
    "note": "接第 6 章结尾打开保险箱的瞬间，Julian 突然伸手按住柜门"
  }
}
```

---

## 六、 脚本（`cws check`）强校验规则

| 检查项 | 违规判定 | 处置结果 |
|---|---|---|
| **付费点软钩** | `paywall: true` 且使用 `button` 或 `question` | **错误（Error）**：付费点必须为硬钩 |
| **付费点强度不足** | `paywall: true` 且强度 `< paywall_min_strength`（默认 4 或 5） | **错误（Error）** |
| **低于平台强度下限** | 连载 App 章节强度 `< min_strength`（默认 3） | **告警（Warn）** |
| **连续弱钩** | 连载模式下连续弱钩（强度 ≤ 2）超过平台 `max_weak_run`（默认 0~1） | **告警（Warn）**：严重警告弃读风险 |
| **平台禁用类型** | 使用了平台 `disallowed_types` 中的类型（如短剧禁用 `button`） | **错误（Error）** |
| **同类型连续** | 同一钩子类型连续 2 章告警，连续 3 章报错 | **告警 / 错误** |
| **钩子未落章尾** | `hook.keywords` 没出现在章尾设定字数内（半拍截断失败） | **告警（Warn）** |
| **开头未接钩子** | 下章开头未出现 `catch.keywords` | **错误（Error）** |
| **章尾总结升华句** | 命中风格库的总结句（如“一切才刚刚开始”） | **错误（Error）** |
