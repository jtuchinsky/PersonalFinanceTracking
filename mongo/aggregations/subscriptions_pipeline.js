const TENANT_ID="__TENANT_ID__";
db.getCollection("transactions").aggregate([
  { $match: { tenantId: TENANT_ID, amount: { $lt: 0 } } },
  { $addFields: { merchantKey: { $ifNull: ["$merchant", "$descriptionRaw"] } } },
  { $setWindowFields: {
      partitionBy: { merchantKey: "$merchantKey" },
      sortBy: { postedAt: 1 },
      output: { prevDate: { $shift: { output: "$postedAt", by: -1 } }, prevAmount: { $shift: { output: "$amount", by: -1 } } }
  }},
  { $addFields: {
      gapDays: { $divide: [ { $subtract: [ { $toDate: "$postedAt" }, { $toDate: "$prevDate" } ] }, 86400000 ] },
      amountDelta: { $abs: { $subtract: ["$amount", "$prevAmount"] } }
  }},
  { $match: { prevDate: { $ne: null } } },
  { $group: {
      _id: { merchantKey: "$merchantKey" },
      avgGap: { $avg: "$gapDays" }, stdGap: { $stdDevPop: "$gapDays" }, cnt: { $sum: 1 },
      avgAmount: { $avg: "$amount" }, lastSeenAt: { $max: "$postedAt" }
  }},
  { $addFields: {
      cadence: { $switch: { branches: [
        { case: { $and: [ { $gte: ["$avgGap", 27] }, { $lte: ["$avgGap", 33] } ] }, then: "monthly" },
        { case: { $and: [ { $gte: ["$avgGap", 6] }, { $lte: ["$avgGap", 8] } ] }, then: "weekly" },
        { case: { $and: [ { $gte: ["$avgGap", 85] }, { $lte: ["$avgGap", 95] } ] }, then: "quarterly" }
      ], default: "unknown" } },
      confidence: { $min: [1, { $divide: ["$cnt", 6] }] }
  }},
  { $project: {
      tenantId: TENANT_ID, merchantNormalized: "$_id.merchantKey", cadence: 1, lastSeenAt: 1, avgAmount: 1,
      nextExpectedAt: { $dateToString: { format: "%Y-%m-%d", date: { $dateAdd: { startDate: { $toDate: "$lastSeenAt" }, unit: "day", amount: { $round: "$avgGap" } } } } },
      confidence: 1, status: { $literal: "candidate" }
  }},
  { $merge: { into: "subscriptions", on: ["tenantId","merchantNormalized"], whenMatched: "replace", whenNotMatched: "insert" } }
])
