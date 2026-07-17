---
name: dictionary-lookup-api
description: 系统级字典查询提示词。任何业务场景中，只要字段是字典 / 枚举 / 下拉值，就适用本 skill

---

# 系统级字典查询规则

## 适用范围

- 任何业务场景中，所有的字典都使用本 skill 去查询字典项值


## 前置条件

- API 地址：`http://172.20.7.243:8000/ai-api`
- 认证：`Authorization: Sys <JWT_TOKEN>`，token 使用统一认证，调用前检查 `exp` 是否过期
- 公司：`companyId` 由用户提供或从 token payload 的 `companyId` 读取
- 可选资源：`archResId` 由业务页面或用户提供；无明确要求时可不传

## 输入

- `dType`（必填）：字典类型 code
- `dKey`（可选）：待翻译或待匹配的值；不传则返回全部字典项
- `companyId`（必填）：公司 ID；优先使用用户显式提供值，否则从 token payload 读取
- `archResId`（可选）：菜单 / 资源 ID；仅当调用方明确提供或业务页面请求包含时传入

## HTTP 请求

优先使用系统字典分页查询接口：

```http
POST {BASE}/microarch/sys/sysDictHead/find
Content-Type: application/json
Authorization: Sys <JWT_TOKEN>
companyId: <COMPANY_ID>
platform: PC

{
  "entity": {
    "lang": "zh_CN",
    "archResId": "<ARCH_RES_ID>"
  },
  "where": [
    {
      "field": "dtype",
      "opt": "like",
      "value": "<dType>",
      "assemble": "and"
    }
  ],
  "pageNum": 0,
  "pageSize": 10,
  "orderBy": "lastmodifiedTime DESC"
}
```

说明：

- 如果没有 `archResId`，`entity` 只传 `{"lang":"zh_CN"}`。
- 返回 `rows[].sysDicts` 即字典项列表，`code=10000` 为成功。
- 不再优先使用 `/findByDcode`。该接口在部分字典上会返回 `entity=null` 并触发后端 `Session.evict()` 空指针。
- 如需 Cookie，可补充：`Cookie: user=<用户名>; token=<JWT_TOKEN>`，但字典查询以 `Authorization` 与 `companyId` 为准。

## 通用解析规则

1. `code ≠ 10000` → 判定查询失败，输出 `msg`，不得继续保存
2. `rows` 为空 → 输出 **"未找到数据字典：{dType}，请先进行同步！"**，不得继续保存
3. 若返回多条 `rows`：
   - 优先选择 `dtype == dType` 的精确匹配项
   - 若没有精确匹配项，不得猜测，输出候选 `dtype / dname` 并要求确认
4. 取命中字典头的 `sysDicts` 作为字典项列表
5. `sysDicts` 为空 → 输出 **"未找到数据字典项：{dType}，请先进行同步！"**，不得继续保存
6. 未传 `dKey` → 返回全部字典项列表与 `dkey -> dvalue` 映射
7. 精确匹配 `dkey == dKey` → 直接返回该项
8. 若待匹配值等于某项 `dvalue` → 返回该项 `dkey`
9. `dKey` 含 `,` `:` `;` 分隔符 → 拆分后逐项解析；对每一项分别返回结果
10. 未命中任何字典项，但字段允许默认回填 → 取 `sysDicts[0].dkey` 作为保存值，并标记为“字典默认值”

## 通用保存规则

- 展示给用户：`dvalue`
- 写入保存字段：`dkey`
- 默认值：字典第一项 `dkey`
- 禁止行为：硬编码字典项、猜测字典值、把 `未识别` 写入字典字段

## 通用输出检查点

每次查询完成后，至少输出：

- 字段名
- `dType`
- 待匹配原值
- 命中的 `dkey / dvalue`
- 若未命中，是否回填为第一项 `dkey`
- 当前字段是否已满足保存条件

## 失败判定

出现以下任一情况，视为本步骤失败：

- 未查询字典就直接构造保存值
- 字典字段保存的是中文展示值而不是 `dkey`
- 未命中时写入 `未识别`
