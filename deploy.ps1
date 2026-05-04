# Rowen: 'Commencing deployment sequence for The Archetype Atlas...'
$ServiceName = "archetype-atlas"
$Region = "us-central1"

Write-Host "Rowen: 'Initiating orbital uplink to Google Cloud Run...'" -ForegroundColor Cyan

# Deploy to Cloud Run as requested
gcloud run deploy $ServiceName `
    --source . `
    --region $Region `
    --allow-unauthenticated `
    --set-secrets=GOOGLE_API_KEY=GEMINI_API_KEY:latest `
    --max-instances 1 `
    --min-instances 0

if ($LASTEXITCODE -eq 0) {
    # Retrieve the final Service URL
    $url = gcloud run services describe $ServiceName --region $Region --format='value(status.address.url)'
    
    Write-Host "`nRowen: 'Synthesis complete. The Atlas Engine is live.'" -ForegroundColor Cyan
    Write-Host "Service URL: " -NoNewline
    # 'Cyber Lime' achieved via bright Green in standard PowerShell
    Write-Host $url -ForegroundColor Green 
} else {
    Write-Host "`nRowen: 'Deployment interrupted. Diagnostics required.'" -ForegroundColor Red
}
