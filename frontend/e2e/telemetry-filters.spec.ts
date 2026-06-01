import { test, expect } from '@playwright/test'

test('telemetry filters persist in URL and survive reload', async ({ page }) => {
  await page.route('**/content-items', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/connectors/diagnostics', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ connectors: [] }) })
  })

  await page.route('**/runs/telemetry/summary**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_runs: 1,
        successful_runs: 1,
        failed_runs: 0,
        total_estimated_cost_usd: 0.01,
        total_estimated_tokens: 100,
        budget_limited_runs: 0,
        budget_exceeded_runs: 0,
        by_run_type: { produce_content: 1 },
      }),
    })
  })

  await page.goto('/telemetry')
  await expect(page.getByRole('heading', { name: 'Run Telemetry' })).toBeVisible()

  await page.getByLabel('Run type').selectOption('produce_content')
  await page.getByLabel('From').fill('2026-06-01')
  await page.getByLabel('To').fill('2026-06-30')
  await page.getByRole('button', { name: 'Apply Filters' }).click()

  await expect(page).toHaveURL(/run_type=produce_content/)
  await expect(page).toHaveURL(/date_from=2026-06-01/)
  await expect(page).toHaveURL(/date_to=2026-06-30/)

  await page.reload()
  await expect(page.getByLabel('Run type')).toHaveValue('produce_content')
  await expect(page.getByLabel('From')).toHaveValue('2026-06-01')
  await expect(page.getByLabel('To')).toHaveValue('2026-06-30')
})
