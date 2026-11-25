# Transformer inquiry ready for review

Owner: Renegade integration. Status: **draft only; not sent; no purchase authorization**. Prepared 24 November 2026. Recipient: **mable@mableaudio.com**, published on the [Mable contact page](https://www.mableaudio.com/en/contact.asp). Request one prototype set, with delivery to Shanghai city only; no personal address, project files or payment details are included.

Purpose: obtain missing electrical, mechanical and domestic sales evidence needed before choosing parts and laying out the populated chassis. The values below are requests/reference targets, not an approved manufacturing specification. Supplier alternatives must be reanalysed before acceptance.

## Proposed subject

咨询：25W EL34吉他音箱变压器，120/220V两档，单套样机，上海交货

## Proposed message

您好，

我们正在设计一台约25W的EL34推挽吉他音箱，使用2只EL34和4只ECC83/12AX7，另有低压混响及控制电路。希望采购一套样机用变压器，可在中国网站或贵司淘宝店下单，发往上海。希望采用可靠、价格适中的产品，不需要高价Hi-Fi规格。目前仅咨询资料和报价，不是下单或定制生产确认。

请优先推荐现货标准型号；如果需要定制，请分别说明价格、起订量和交期。

**1. 输出变压器（1只）**

- 约25W额定音频输出，EL34推挽。现有电路参考初级全绕组阻抗7.6kΩ、中心抽头，次级公共端/4Ω/8Ω，4Ω端用于负反馈。
- 贵司MATR0233网页的4–6.6kΩ范围与7.6kΩ不同。如无7.6kΩ型号，请列出可供应的6.6kΩ、8kΩ或8.5kΩ等型号，不能直接视为等效替换，我们会重新计算。
- 吉他最低基音约82Hz，不强求20Hz全功率Hi-Fi指标。请注明额定功率对应频率、失真、温升和测试条件。过载时可能超过25W，请说明允许的短时/连续功率、持续时间和负载条件，及可选40–50W型号的价格和体积。
- 请提供初级各半绕组额定直流电流、允许不平衡电流、初级/次级直流电阻、额定绝缘/耐压及相位/线色图。
- 如有开路电感、漏感、绕组电容或带8Ω负载的幅频/相频数据，请提供并注明测量端子、频率、电压及直流偏置。没有的数据请直接注明未测试。

**2. 主电源变压器（1只）**

- 需要120V/60Hz和220V/50Hz两档。拟按108–132V及198–242V范围检查，请确认产品允许的实际输入范围和温升条件。如推荐115/230V绕组，请明确是否支持这些工作范围，不能只按标签电压推断。
- 当前参考高压绕组300–0–300VAC，目录参考电流173mA。请明确贵司标注的是交流绕组RMS电流还是整流后的直流负载电流，并给出空载电压及典型负载电压/温升，供我们选型复核。
- 灯丝绕组6.3VAC：电子管额定合计4.2A，含平衡电阻及预留指示灯约4.38A。参考选用至少5A绕组，请提供空载/4.4A负载电压、额定电流与启动承受能力。
- 需要约50VAC的固定负偏压绕组/抽头；请说明可供应结构、额定电流、与高压中心抽头的关系及隔离方式。
- 如可以增加独立低压辅助绕组，请单列价格、尺寸和各绕组同时负载时的电压数据，供与独立辅助变压器比较。

**3. 辅助电源变压器（独立1只，或主电源的独立绕组方案）**

- 同样需要120/220V两档、相应60/50Hz输入。拟使用带中心点的两组相同次级绕组，为±15V音频、12V继电器及5V逻辑供电。
- 请推荐约2×16VAC或2×18VAC、每组至少0.5A的标准型号，提供空载、轻载、0.25A及0.5A负载电压，以及各一次电压/频率下的数据。最终电压和容量必须根据这些资料确认；目前不授权按这些参考值生产。
- 我们采用电容输入整流，正负负载不相等。请说明该额定电流是否适用于此工况，提供绕组电阻/温升/调压率及公差。若只能给典型值，请注明。

**三个部分均请提供：**

1. 准确型号、绕组接线/相位图、绝缘等级、耐压测试条件、建议一次保险丝及内部温度保护信息。
2. 完整尺寸图：含外罩、安装耳、螺孔/长孔尺寸和间距、引线出口、安装件、重量；需要据此设计固定金属机架，不能只给铁芯尺寸。
3. 单只及整套人民币含税价格、现货数量/交期、样机最小订购量、上海运费，以及可下单的中国网站/淘宝商品链接。

谢谢！请先提供资料和报价，我们确认设计后再决定是否购买。

## Internal acceptance notes — not part of the message

Treat a quote as commercial evidence, not electrical acceptance. Reconcile loaded voltages, ratio and parasitics with the existing transformer/feedback and auxiliary supply models. Confirm all dimensions before three-board/chassis consolidation. Keep heavy magnetics on structural metal; no support on the removable wooden rear. Do not send source files or add a street address without need and authorization. Obtain explicit sending instruction; the standing feedback workflow also preserves the user's immediate send-confirmation procedure for mail.
