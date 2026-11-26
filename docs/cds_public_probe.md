# Public single-company CDS trades (SEC rule, DTCC repository): the probe

Day 2026-11-24, address `https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDITS_2026_11_24.zip`: 1,225 rows, 110 columns.

Columns: `Dissemination Identifier`, `Original Dissemination Identifier`, `Action type`, `Event type`, `Event timestamp`, `Amendment indicator`, `Asset Class`, `Product name`, `Cleared`, `Mandatory clearing indicator`, `Execution Timestamp`, `Effective Date`, `Expiration Date`, `Maturity date of the underlier`, `Non-standardized term indicator`, `Platform identifier`, `Prime brokerage transaction indicator`, `Block trade election indicator`, `Large notional off-facility swap election indicator`, `Notional amount-Leg 1`, `Notional amount-Leg 2`, `Notional currency-Leg 1`, `Notional currency-Leg 2`, `Notional quantity-Leg 1`, `Notional quantity-Leg 2`, `Total notional quantity-Leg 1`, `Total notional quantity-Leg 2`, `Quantity frequency multiplier-Leg 1`, `Quantity frequency multiplier-Leg 2`, `Quantity unit of measure-Leg 1`, `Quantity unit of measure-Leg 2`, `Quantity frequency-Leg 1`, `Quantity frequency-Leg 2`, `Notional amount in effect on associated effective date-Leg 1`, `Notional amount in effect on associated effective date-Leg 2`, `Effective date of the notional amount-Leg 1`, `Effective date of the notional amount-Leg 2`, `End date of the notional amount-Leg 1`, `End date of the notional amount-Leg 2`, `Call amount`, `Call currency`, `Put amount`, `Put currency`, `Exchange rate`, `Exchange rate basis`, `First exercise date`, `Fixed rate-Leg 1`, `Fixed rate-Leg 2`, `Option Premium Amount`, `Option Premium Currency`, `Price`, `Price unit of measure`, `Spread-Leg 1`, `Spread-Leg 2`, `Spread currency-Leg 1`, `Spread currency-Leg 2`, `Strike Price`, `Strike price currency/currency pair`, `Post-priced swap indicator`, `Price currency`, `Price notation`, `Spread notation-Leg 1`, `Spread notation-Leg 2`, `Strike price notation`, `Fixed rate day count convention-leg 1`, `Fixed rate day count convention-leg 2`, `Floating rate day count convention-leg 1`, `Floating rate day count convention-leg 2`, `Floating rate reset frequency period-leg 1`, `Floating rate reset frequency period-leg 2`, `Floating rate reset frequency period multiplier-leg 1`, `Floating rate reset frequency period multiplier-leg 2`, `Other payment amount`, `Fixed rate payment frequency period-Leg 1`, `Floating rate payment frequency period-Leg 1`, `Fixed rate payment frequency period-Leg 2`, `Floating rate payment frequency period-Leg 2`, `Fixed rate payment frequency period multiplier-Leg 1`, `Floating rate payment frequency period multiplier-Leg 1`, `Fixed rate payment frequency period multiplier-Leg 2`, `Floating rate payment frequency period multiplier-Leg 2`, `Other payment type`, `Other payment currency`, `Settlement currency-Leg 1`, `Settlement currency-Leg 2`, `Settlement location`, `Collateralisation category`, `Custom basket indicator`, `Index factor`, `Underlier ID-Leg 1`, `Underlier ID-Leg 2`, `Underlier ID source-Leg 1`, `Underlying Asset Name`, `Underlying asset subtype or underlying contract subtype-Leg 1`, `Underlying asset subtype or underlying contract subtype-Leg 2`, `Embedded Option type`, `Option Type`, `Option Style`, `Package indicator`, `Package transaction price`, `Package transaction price currency`, `Package transaction price notation`, `Package transaction spread`, `Package transaction spread currency`, `Package transaction spread notation`, `Physical delivery location-Leg 1`, `Delivery Type`, `Unique Product Identifier`, `UPI FISN`, `UPI Underlier Name`

| company | trades that day that name it |
|---|---|
| Oracle | 52 |
| Meta | 7 |
| Alphabet | 25 |
| Microsoft | 6 |
| Amazon | 10 |
| Apple | 0 |
| Nvidia | 15 |
| Broadcom | 24 |
| Intel | 0 |
| AMD | 15 |
| Micron | 0 |
| IBM | 0 |
| Cisco | 0 |
| Dell | 3 |
| CoreWeave | 14 |
| Tesla | 1 |
| Qualcomm | 0 |

Nothing was kept on disk. Before any daily collection: read DTCC's terms for this public data, and check the columns that hold the company, the spread and the time.
