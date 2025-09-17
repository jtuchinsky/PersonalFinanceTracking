const TENANT_ID="__TENANT_ID__";
db.getCollection("transactions").aggregate([
  { $match: { tenantId: TENANT_ID } },
  { $addFields: { month: { $dateToString: { format: "%Y-%m", date: { $toDate: "$postedAt" } } } } },
  { $group: { _id: { month: "$month", categoryId: "$categoryId" }, total: { $sum: "$amount" }, count: { $sum: 1 } } },
  { $project: { _id: 0, tenantId: TENANT_ID, month: "$_id.month", categoryId: "$_id.categoryId", total: 1, count: 1 } },
  { $merge: { into: "rollups_category_month", on: ["tenantId","month","categoryId"], whenMatched: "replace", whenNotMatched: "insert" } }
])
