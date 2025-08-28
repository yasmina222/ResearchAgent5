# Protocol Education Competitive Intelligence System

A **lethal research assistant** for Protocol Education consultants to gather verified contact information and competitive intelligence at scale.

## 🎯 Mission

Help Protocol Education win back market share by providing:
- **Verified contact details** for Deputy Heads, Assistant Heads, Business Managers, and SENCOs
- **Competitive intelligence** on which agencies serve each school
- **Conversation starters** based on recent events, Ofsted ratings, and achievements
- **Confidence scoring** so consultants know which data to trust

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or create project directory
cd Protocol_Intelligence

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Command Line Usage

```bash
# Single school lookup
python main.py school "St Mary's Primary School"
python main.py school "Oakwood Academy" --website https://oakwood.edu --force

# Borough-wide sweep
python main.py borough "Camden" --type primary
python main.py borough "Westminster" --type all --format csv

# Cache management
python main.py cache stats
python main.py cache clear
```

### 3. Web Interface (Streamlit)

```bash
# Launch web interface
streamlit run streamlit_app.py

# Access at http://localhost:8501
```

## 📊 Features

### Core Intelligence Gathering
- **Multi-source data collection** from school websites
- **AI-powered extraction** using GPT-4o for HTML/images
- **Smart model selection** to optimize costs
- **Contact verification** via SMTP ping and phone normalization
- **Pattern detection** for email generation
- **Confidence scoring** based on data quality

### Verification Tools
- `smtp_ping()` - Verify email addresses without sending
- `normalize_phone()` - Convert UK numbers to E.164 format
- `pattern_tester()` - Generate emails from detected patterns

### Competitive Analysis
- Detect agencies from job postings and testimonials
- Identify competitor weaknesses
- Generate win-back strategies
- Track Protocol Education advantages

### Conversation Intelligence
- Recent Ofsted ratings and inspection dates
- School achievements and awards
- Upcoming events and initiatives
- Leadership changes and new hires
- Building projects and expansions

## 💰 Budget Optimization

Designed to process **500+ schools/month within $150 budget**:

- **GPT-4o** for HTML and vision tasks (highest accuracy)
- **GPT-4o-mini** for PDF processing (80% cost reduction)
- **GPT-3.5-turbo** for text-only PDFs (cheapest)
- **24-hour caching** to avoid redundant API calls
- **Batch processing** for borough sweeps

## 📁 Project Structure

```
Protocol_Intelligence/
├── config.py           # System configuration and API keys
├── models.py           # Data models and JSON schemas
├── verification.py     # Contact verification functions
├── scraper.py          # Web scraping with BeautifulSoup
├── ai_engine.py        # OpenAI API integration
├── cache.py            # SQLite caching system
├── processor.py        # Main processing orchestration
├── exporter.py         # CSV/Excel/JSON export
├── main.py             # CLI application
├── streamlit_app.py    # Web interface
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── cache/             # Cache directory (auto-created)
└── outputs/           # Export directory (auto-created)
```

## 🔧 Configuration

Edit `config.py` to customize:

- Model selection for different tasks
- Rate limits and token limits
- Cache TTL (default: 24 hours)
- Email patterns to test
- Competitor keywords
- Output formats

## 📈 Output Formats

### Excel Export (Recommended)
Multi-sheet workbook with:
- **Overview** - Summary of all schools
- **All Contacts** - Detailed contact information
- **Competitor Analysis** - Agency presence
- **Conversation Starters** - Intelligence for calls

### CSV Export
Flat file with all key fields for easy import

### JSON Export
Complete structured data for integration

## 🛡️ Data Quality

Each contact includes:
- **Confidence score** (0-100%)
- **Verification method** used
- **Evidence URLs** for manual verification
- **Last verified** timestamp

Confidence levels:
- 90-100%: Direct website evidence
- 70-89%: Multiple corroborating sources
- 50-69%: Single source with patterns
- 30-49%: Indirect indicators only
- 0-29%: No reliable evidence

## ⚡ Performance

- Single school: ~15-30 seconds
- Borough sweep: ~2-5 minutes for 30 schools
- Cached results: <1 second
- Concurrent processing for batch operations

## 🔒 Security & Compliance

- No storage of personal data beyond cache TTL
- GDPR-compliant (public data only)
- Secure API key handling via environment variables
- Rate limiting to respect websites

## 🐛 Troubleshooting

### "API key not found"
Create `.env` file with:
```
OPENAI_API_KEY=your-key-here
```

### "Rate limit exceeded"
The system automatically handles rate limits. For persistent issues, reduce concurrent workers in `processor.py`.

### "No contacts found"
Some schools have limited online presence. Try:
- Adding `--force` flag to bypass cache
- Checking the website URL is correct
- Running during UK business hours

## 🚧 Future Enhancements

Phase 2 considerations:
- CRM integration (when GDPR resolved)
- LinkedIn integration (if budget allows)
- Historical tracking of changes
- Automated daily/weekly reports
- Slack/Teams notifications

## 📞 Support

For issues or questions:
1. Check logs in `protocol_ci.log`
2. Review cache stats: `python main.py cache stats`
3. Verify API usage hasn't exceeded budget

---

**Built for Protocol Education** 