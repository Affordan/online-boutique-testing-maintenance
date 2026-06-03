Invoke-RestMethod http://localhost:18081/health
Invoke-RestMethod http://localhost:18081/coupons
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:18081/coupons/validate `
  -ContentType "application/json" `
  -Body '{"code":"SAVE10","cart_total":49.99}'
