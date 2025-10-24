# Google Gemini 2.5 Flash Integration Guide

## Overview

AetherSegment AI uses **Google Gemini 2.5 Flash** via Vertex AI for all natural language processing and campaign interpretation tasks. This provides enterprise-grade AI capabilities with tight Google Cloud Platform integration.

## Why Gemini 2.5 Flash?

### Advantages

1. **Native GCP Integration**
   - Same authentication as BigQuery
   - No additional API keys needed
   - Unified billing and monitoring

2. **Enterprise Features**
   - Built-in quota management
   - Automatic scaling
   - Regional deployment options
   - Enhanced security and compliance

3. **Cost-Effective**
   - Competitive pricing
   - No separate subscription needed
   - Pay-per-use model

4. **Performance**
   - Low latency (< 2 seconds typical response)
   - JSON mode for structured output
   - High throughput for production workloads

## Setup Requirements

### 1. Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

Or via Console:
1. Go to [Vertex AI](https://console.cloud.google.com/vertex-ai)
2. Click "Enable API"

### 2. Grant Service Account Permissions

Your service account needs the **Vertex AI User** role:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

Or via Console:
1. Go to IAM & Admin
2. Find your service account
3. Click "Edit"
4. Add role: "Vertex AI User"

### 3. Configure Region

Set the `GOOGLE_CLOUD_REGION` environment variable (default: `us-central1`):

```env
GOOGLE_CLOUD_REGION=us-central1
```

Available regions with Gemini support:
- `us-central1` (Iowa) - Recommended
- `us-east4` (Virginia)
- `europe-west1` (Belgium)
- `asia-southeast1` (Singapore)

## Model Configuration

### Current Model

**gemini-2.5-flash** - Gemini 2.5 Flash

Benefits:
- Latest generation model with improved reasoning
- Excellent for structured output and complex tasks
- Enhanced performance over previous versions
- Better understanding of nuanced marketing language

### Alternative Models

You can change the model in `backend/config.py`:

```python
GEMINI_MODEL = 'gemini-2.5-flash'  # Default - fast and efficient
GEMINI_MODEL = 'gemini-2.5-pro'  # For more complex reasoning
GEMINI_MODEL = 'gemini-1.5-flash'  # For stable production use
GEMINI_MODEL = 'gemini-1.5-pro'  # For legacy compatibility
```

### Generation Parameters

Configured in `backend/config.py`:

```python
GEMINI_TEMPERATURE = 0.3  # Lower = more deterministic
GEMINI_MAX_OUTPUT_TOKENS = 2048  # Maximum response length
```

## How It Works

### 1. Initialization

The `CampaignIntentInterpreter` initializes Vertex AI on startup:

```python
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

vertexai.init(
    project=Config.GOOGLE_CLOUD_PROJECT,
    location=Config.GOOGLE_CLOUD_REGION
)

model = GenerativeModel(Config.GEMINI_MODEL)
```

### 2. Structured Output

Gemini is configured to return JSON directly:

```python
generation_config = GenerationConfig(
    temperature=0.3,
    max_output_tokens=2048,
    response_mime_type="application/json"
)
```

### 3. Campaign Analysis

When a user enters a campaign objective:

```
"Increase conversion for abandoned carts by 20% within 48 hours"
```

Gemini extracts structured data:

```json
{
  "campaign_goal": "conversion",
  "target_behavior": "abandoned_cart",
  "metric_target": {
    "type": "conversion_rate_increase",
    "value": 0.20
  },
  "time_constraint": "48_hours_post_abandonment",
  "proposed_intervention": "personalized_discount_offer"
}
```

## Monitoring & Debugging

### View Requests in Console

1. Go to [Vertex AI Dashboard](https://console.cloud.google.com/vertex-ai)
2. Navigate to "Model Garden" → "Gemini"
3. View request history and metrics

### Enable Detailed Logging

Add to your backend code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- Request prompts
- Response content
- Token usage
- Latency metrics

### Check Quotas

View your quotas:
```bash
gcloud ai quotas list --region=us-central1
```

Default quotas are usually sufficient for prototypes (1000+ requests/minute).

## Cost Estimation

### Gemini 2.5 Flash Pricing (as of 2024)

**Input**: ~$0.00001875 per 1K characters
**Output**: ~$0.000075 per 1K characters

### Typical Campaign Analysis

- Input: ~1,000 characters (prompt + objective)
- Output: ~500 characters (JSON response)

**Cost per analysis**: ~$0.00005 (negligible)

For 10,000 campaign analyses/month: **~$0.50**

### Compare to OpenAI GPT-4

- GPT-4: ~$0.03 per request
- Gemini 2.5 Flash: ~$0.00005 per request
- **Savings: 99.8%**

## Troubleshooting

### Error: "Vertex AI API not enabled"

**Solution:**
```bash
gcloud services enable aiplatform.googleapis.com
```

### Error: "Permission denied"

**Solution:**
Check service account has "Vertex AI User" role:
```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.role:roles/aiplatform.user"
```

### Error: "Region not supported"

**Solution:**
Use a supported region:
```env
GOOGLE_CLOUD_REGION=us-central1
```

### Slow Response Times

**Possible causes:**
- Region mismatch (use closest region)
- Network latency
- Model warm-up (first request is slower)

**Solutions:**
- Choose nearest supported region
- Implement request caching
- Use connection pooling

## Advanced Features

### Streaming Responses

For real-time UI updates:

```python
response = model.generate_content(
    prompt,
    generation_config=generation_config,
    stream=True
)

for chunk in response:
    print(chunk.text)
```

### Safety Settings

Configure content filtering:

```python
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
}

response = model.generate_content(
    prompt,
    safety_settings=safety_settings
)
```

### Function Calling

For more complex integrations:

```python
from vertexai.generative_models import FunctionDeclaration, Tool

# Define function
analyze_segment = FunctionDeclaration(
    name="analyze_customer_segment",
    description="Analyzes customer segment characteristics",
    parameters={...}
)

tool = Tool(function_declarations=[analyze_segment])
```

## Migration from OpenAI

If you need to switch back to OpenAI:

1. Install OpenAI SDK:
   ```bash
   pip install openai==1.3.7
   ```

2. Update `backend/config.py`:
   ```python
   OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
   LLM_MODEL = 'gpt-4'
   ```

3. Modify `backend/models/intent_interpreter.py`:
   ```python
   import openai
   
   response = openai.chat.completions.create(
       model='gpt-4',
       messages=[...],
       response_format={"type": "json_object"}
   )
   ```

## Best Practices

1. **Use JSON Mode**
   - Always set `response_mime_type="application/json"`
   - Provides structured, parseable output

2. **Optimize Prompts**
   - Be specific and detailed
   - Include examples in prompt
   - Use clear structure

3. **Handle Errors Gracefully**
   - Implement retry logic
   - Fallback to defaults
   - Log all errors

4. **Monitor Usage**
   - Track request counts
   - Monitor latency
   - Set up alerts for quota limits

5. **Version Control**
   - Pin model versions for production
   - Test new models in staging first
   - Document model changes

## Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Quotas & Limits](https://cloud.google.com/vertex-ai/docs/quotas)

## Support

For issues with Gemini integration:

1. Check [Vertex AI Status](https://status.cloud.google.com/)
2. Review [Release Notes](https://cloud.google.com/vertex-ai/docs/release-notes)
3. Contact [GCP Support](https://cloud.google.com/support)

---

**Gemini 2.5 Flash provides enterprise-grade AI capabilities with seamless GCP integration, making it the ideal choice for AetherSegment AI.**

