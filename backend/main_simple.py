import os
import time
from datetime import datetime

from agno.agent import Agent
from agno.exceptions import ModelProviderError
from agno.models.google import Gemini

from config import get_google_api_key
from pdf_generator import generate_pdf_report

GOOGLE_API_KEY = get_google_api_key(required=True)

# Create a single comprehensive agent (instead of 4 separate agents)
simple_analyst = Agent(
    name="Investment Analyst",
    model=Gemini(
        id="gemini-2.0-flash-001", 
        api_key=GOOGLE_API_KEY,
    ),
    instructions=[
        "You are an expert investment analyst",
        "Provide comprehensive investment analysis reports",
        "Cover: company overview, financial metrics, market sentiment, risks, and recommendations",
        "Be thorough but concise",
        "Use clear, professional language suitable for investors"
    ],
)

def generate_investment_report_simple(ticker: str, company_name: str = None, save_to_file: bool = True):
    """
    Generate investment report using a single agent (simpler, fewer API calls).
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        company_name: Full company name (optional)
        save_to_file: Whether to save the report to a file
    """
    
    print(f"\n🚀 Starting investment analysis for {ticker}...\n")
    
    # Create comprehensive analysis prompt
    analysis_prompt = f"""
    Create a comprehensive investment analysis report for {ticker} ({company_name or 'company name to be determined'}).
    
    Your report should include:
    
    1. EXECUTIVE SUMMARY
       - Quick recommendation (Buy/Hold/Sell)
       - Key highlights and concerns
       - Target price if applicable
    
    2. COMPANY OVERVIEW
       - Business description
       - Main products/services
       - Market position
       - Recent developments
    
    3. FINANCIAL ANALYSIS
       - Revenue and earnings trends
       - Profitability metrics (margins, ROE, ROA)
       - Balance sheet health
       - Cash flow analysis
       - Key financial ratios
    
    4. MARKET & SENTIMENT ANALYSIS
       - Recent stock performance
       - Analyst ratings and price targets
       - Market sentiment
       - News impact
    
    5. GROWTH PROSPECTS
       - Growth drivers
       - Market opportunities
       - Competitive advantages
       - Future outlook
    
    6. RISK ASSESSMENT
       - Business risks
       - Financial risks
       - Market risks
       - Regulatory/legal risks
    
    7. VALUATION
       - Current valuation metrics (P/E, P/S, P/B, etc.)
       - Comparison to industry peers
       - Historical valuation trends
       - Fair value assessment
    
    8. INVESTMENT RECOMMENDATION
       - Clear Buy/Hold/Sell recommendation
       - Rationale for recommendation
       - Investment horizon
       - Key factors to monitor
    
    9. DISCLAIMERS
       - This is for informational purposes only
       - Not financial advice
       - Past performance doesn't guarantee future results
    
    Format the report professionally with clear sections and bullet points where appropriate.
    Use the current date: {datetime.now().strftime('%Y-%m-%d')}
    """
    
    # Execute analysis with robust retry logic
    print("🔍 Analyzing investment opportunity...")
    max_retries = 3
    retry_delay = 60  # Start with 60 seconds
    
    result = None
    for attempt in range(max_retries):
        try:
            result = simple_analyst.run(analysis_prompt)
            print(f"✅ Analysis complete\n")
            break
        except (ModelProviderError, Exception) as e:
            error_str = str(e)
            
            # Check for network connectivity errors
            is_network_error = (
                "getaddrinfo failed" in error_str or
                "11001" in error_str or
                "ConnectError" in error_str or
                "Connection refused" in error_str.lower() or
                "Network is unreachable" in error_str.lower() or
                "Failed to establish" in error_str.lower()
            )
            
            # Check for rate limit (429), resource exhausted, or service unavailable (503)
            is_retryable = (
                "429" in error_str or 
                "RESOURCE_EXHAUSTED" in error_str or
                "503" in error_str or
                "Service Unavailable" in error_str or
                "UNAVAILABLE" in error_str or
                "overloaded" in error_str.lower()
            )
            
            if is_network_error:
                print(f"\n❌ NETWORK CONNECTION ERROR (attempt {attempt + 1}/{max_retries})")
                print(f"   Cannot reach Gemini API servers")
                print("\n🔍 TROUBLESHOOTING STEPS:")
                print("   1. 🌐 Check your internet connection")
                print("      - Open a web browser and visit google.com")
                print("      - If that works, try: https://generativelanguage.googleapis.com")
                print("\n   2. 🔥 Check your firewall/antivirus")
                print("      - Temporarily disable firewall/antivirus and try again")
                print("      - Or add Python/this script to firewall exceptions")
                print("\n   3. 🌍 Check proxy settings (if on corporate network)")
                print("      - You may need to configure proxy settings")
                print("      - Contact your IT department if needed")
                print("\n   4. 📡 DNS issues")
                print("      - Try flushing DNS cache:")
                print("        ipconfig /flushdns")
                print("      - Try using Google DNS (8.8.8.8)")
                print("\n   5. 🔌 VPN issues")
                print("      - If using VPN, try disconnecting/reconnecting")
                print("      - Or try without VPN")
                
                if attempt < max_retries - 1:
                    wait_time = 30  # Shorter wait for network issues
                    print(f"\n   ⏳ Waiting {wait_time} seconds before retry...")
                    print(f"      (This gives you time to check your connection)")
                    time.sleep(wait_time)
                    print("\n🔄 Retrying connection...")
                else:
                    print("\n❌ Unable to connect after multiple attempts.")
                    print("   Please fix your network connection and try again.")
                    raise Exception("Network connection error: Cannot reach Gemini API servers. Check your internet connection, firewall, or proxy settings.") from e
            elif is_retryable:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff: 60s, 120s, 240s
                    
                    # Provide specific error message
                    if "503" in error_str or "Service Unavailable" in error_str or "overloaded" in error_str.lower():
                        print(f"⚠️  Service temporarily unavailable (attempt {attempt + 1}/{max_retries})")
                        print(f"   The API server is overloaded or under maintenance.")
                    else:
                        print(f"⏳ Rate limit exceeded (attempt {attempt + 1}/{max_retries})")
                    
                    print(f"   Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    print("🔄 Retrying analysis...")
                else:
                    print(f"\n❌ Failed after {max_retries} attempts.")
                    print("\n💡 SOLUTIONS:")
                    print("   1. ⏰ Wait 5-10 minutes and try again (server may be temporarily overloaded)")
                    print("   2. 🔄 Try analyzing a different company")
                    print("   3. 💳 Upgrade to Gemini API paid tier for better availability")
                    print("   4. 🌐 Check Gemini API status: https://status.cloud.google.com/")
                    raise Exception(f"API unavailable after {max_retries} retry attempts. Please try again later.") from e
            else:
                print(f"❌ Error during analysis: {error_str}")
                raise e
    
    # Check if we got a result
    if result is None:
        raise Exception("Analysis failed: No result returned after retries")
    
    # Save report if requested
    if save_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"reports/output/{ticker}_simple_report_{timestamp}.md"
        
        # Create directory if it doesn't exist
        os.makedirs("reports/output", exist_ok=True)
        
        # Save Markdown version
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(f"# Investment Analysis Report: {ticker}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analysis Type: Simple (Single Agent)\n\n")
            f.write("---\n\n")
            f.write(result.content)
        
        print(f"💾 Markdown report saved to: {md_filename}")
        
        # Generate PDF version
        try:
            print("📄 Generating professional PDF report...")
            pdf_filename = generate_pdf_report(ticker, company_name, result.content)
            print(f"✅ PDF report saved to: {pdf_filename}\n")
        except Exception as e:
            print(f"⚠️  PDF generation failed: {str(e)}")
            print(f"   Markdown report is still available at: {md_filename}\n")
    
    return {
        "ticker": ticker,
        "analysis": result.content,
        "timestamp": datetime.now().isoformat()
    }

def display_menu():
    """Display interactive menu for company selection"""
    print("\n" + "="*80)
    print("📊 SIMPLE INVESTMENT ANALYZER")
    print("="*80)
    print("✅ OPTIMIZED FOR FREE TIER: Uses only 1 agent (fewer API calls)")
    print("💡 For full multi-agent analysis, use main.py")
    print("="*80 + "\n")
    
    # Popular companies list
    popular_companies = {
        "1": {"ticker": "AAPL", "name": "Apple Inc."},
        "2": {"ticker": "MSFT", "name": "Microsoft Corporation"},
        "3": {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)"},
        "4": {"ticker": "AMZN", "name": "Amazon.com Inc."},
        "5": {"ticker": "TSLA", "name": "Tesla Inc."},
        "6": {"ticker": "META", "name": "Meta Platforms Inc. (Facebook)"},
        "7": {"ticker": "NVDA", "name": "NVIDIA Corporation"},
        "8": {"ticker": "NFLX", "name": "Netflix Inc."},
        "9": {"ticker": "AMD", "name": "Advanced Micro Devices Inc."},
        "10": {"ticker": "BABA", "name": "Alibaba Group"},
    }
    
    print("🏢 SELECT A COMPANY TO ANALYZE:\n")
    print("Popular Companies:")
    for key, company in popular_companies.items():
        print(f"  {key:2}. {company['ticker']:6} - {company['name']}")
    
    print("\n  0. Custom ticker (enter your own)")
    print("  Q. Quit")
    
    print("\n" + "="*80)
    
    while True:
        choice = input("\n👉 Enter your choice: ").strip().upper()
        
        if choice == 'Q':
            print("\n👋 Goodbye!")
            return None
        
        elif choice == '0':
            ticker = input("\n📝 Enter stock ticker (e.g., AAPL): ").strip().upper()
            company_name = input("📝 Enter company name (optional, press Enter to skip): ").strip()
            if not ticker:
                print("❌ Ticker cannot be empty!")
                continue
            return {"ticker": ticker, "name": company_name or None}
        
        elif choice in popular_companies:
            return popular_companies[choice]
        
        else:
            print("❌ Invalid choice! Please try again.")

# Example usage
if __name__ == "__main__":
    print("\n🎯 Simple Investment Analyzer - Optimized for Gemini Free Tier")
    print("   Uses fewer API calls = Better for free tier users!\n")
    
    while True:
        choice = display_menu()
        
        if choice is None:
            break
        
        # Single company analysis
        print(f"\n🎯 ANALYZING: {choice['ticker']} - {choice['name'] or 'Company'}")
        print("="*80 + "\n")
        
        try:
            result = generate_investment_report_simple(
                ticker=choice['ticker'],
                company_name=choice['name']
            )
            
            print(f"\n🎉 Investment analysis complete!")
            print(f"📁 Report saved to: reports/output/")
        except Exception as e:
            print(f"\n❌ Analysis failed: {str(e)}")
            print("\n💡 See 503_ERROR_FIX.md for troubleshooting tips")
        
        # Ask if user wants to analyze another company
        print("\n" + "="*80)
        another = input("\n🔄 Analyze another company? (Y/N): ").strip().upper()
        if another != 'Y':
            print("\n👋 Thank you for using Simple Investment Analyzer!")
            break
