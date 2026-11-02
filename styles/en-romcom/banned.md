# en-romcom 禁用表

机器规则在 `style.json`，这里解释原因和替换方法。

| 类别 | 例子 | 换成 |
|---|---|---|
| 把男主写成猛兽 | predator, predatory, lethal, sovereign, apex | 写他做的具体事。他记得她的咖啡点法，比他“像一头猛兽”可怕 |
| 紫色散文 | obsidian eyes, molten, intoxicating, suffocating, unadulterated | 这个人物此刻真会用的比喻 |
| AI 高频词 | tapestry, palpable, testament to, utterly | 直接删，通常不需要替换 |
| 身体套话 | breath hitched, shiver down her spine, heart hammered against her ribs, a breath she didn’t know she was holding | 一个好笑或具体的身体反应：她把同一封邮件读了三遍，还是没读懂 |
| 假转折句式 | It wasn’t X. It was Y. | 直接说 Y |
| 标点喊叫 | `?!`、全大写拟声词 | 让对白本身够响 |
| 中文直译 | take responsibility（负责）、drink vinegar（吃醋）、Director Wang | I’ll make it right；jealous；直呼其名 |
| 低龄化 | little girl | 不用 |

## 章尾禁用

章尾不总结、不升华，不提前告诉读者“一切要变了”。

| 不要 | 要 |
|---|---|
| Little did she know, nothing would ever be the same. | Her phone buzzed. *Bring the file. And the dog.* |
| It was only the beginning. | “You kept the receipt,” he said. “Of course you did.” |

书专属的禁用词写进项目的 `extra_banned`，不要改这个文件。
