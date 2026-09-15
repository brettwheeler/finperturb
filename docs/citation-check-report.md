# Citation check report

- Repository SHA: `456ae771b3df9121d4bbfac0e63fb196414288f2`
- Run (UTC): 2026-09-15 13:19:33Z
- SHA-256 `docs/applicability-matrix.json` (committed bytes at that SHA): `d19bd22b30f25b4d0918daff0ae049c73389e41fd4bf742fd491a928d9b73afd`
- SHA-256 `docs/applicability-matrix-material.json` (committed bytes at that SHA): `a6f33072c433332a01fe8926a06810cecee7e9a7f78c100d3452cf85470ad9b9`

Every cited file is read at the recorded pin with `git show <pin>:<path>`; the working tree is never read.

## Pins

| engine | recorded pin | clone HEAD | matrix | working tree |
|---|---|---|---|---|
| finmem | `be814aa` | `be814aa47970de9bf2fdd6a1d5a60ae5cf361b46` | applicability-matrix.json | working tree has 1 untracked/modified path(s); not read |
| tradingagents | `a33fd4c` | `a33fd4c0f134485a43553a2c23a63cb14adbd88f` | applicability-matrix.json | clean |
| finagent | `17248a0` | `17248a0b8b729ee3e093e30bb7bea7f52181f363` | applicability-matrix.json | clean |
| finmem | `be814aa` | `be814aa47970de9bf2fdd6a1d5a60ae5cf361b46` | applicability-matrix-material.json | working tree has 1 untracked/modified path(s); not read |
| tradingagents | `a33fd4c` | `a33fd4c0f134485a43553a2c23a63cb14adbd88f` | applicability-matrix-material.json | clean |
| finagent | `17248a0` | `17248a0b8b729ee3e093e30bb7bea7f52181f363` | applicability-matrix-material.json | clean |

## docs/applicability-matrix.json

| engine | class | verdict | citation | status | first cited line |
|---|---|---|---|---|---|
| finmem | N1 | run | `puppy/reflection.py:325` | ok | [f"{i[0]}. {i[1].strip()}" for i in zip(short_memory_id, short_memory)] |
| finmem | N1 | run | `puppy/memorydb.py:147-148` | ok | max_len = len(self.universe[symbol]["score_memory"]) |
| finmem | N1 | run | `puppy/embedding.py:10-11` | ok | If the input is larger than the context size, the input is split into chunks of size 'chunk_size' a… |
| finmem | N2 | dropped | `puppy/prompts.py:16` | ok | test_investment_info_prefix = "The ticker of the stock to be analyzed is {symbol} and the current d… |
| finmem | N2 | dropped | `puppy/reflection.py:319-321` | ok | investment_info = test_investment_info_prefix.format( |
| finmem | N3 | run | `puppy/reflection.py:325` | ok | [f"{i[0]}. {i[1].strip()}" for i in zip(short_memory_id, short_memory)] |
| finmem | - | - | `puppy/reflection.py:227-243` | ok | def _add_momentum_info(momentum: int, investment_info: str) -> str: |
| tradingagents | N1 | run_attenuated | `tradingagents/agents/analysts/news_analyst.py:20-28` | ok | tools = [ |
| tradingagents | N1 | run_attenuated | `tradingagents/agents/analysts/news_analyst.py:59-67` | ok | report = "" |
| tradingagents | N1 | run_attenuated | `tradingagents/agents/utils/news_data_tools.py:24` | ok | return route_to_vendor("get_news", ticker, start_date, end_date) |
| tradingagents | N1 | run_attenuated | `tradingagents/dataflows/interface.py:168-198` | ok | def route_to_vendor(method: str, *args, **kwargs): |
| tradingagents | N2 | dropped | `tradingagents/agents/utils/agent_utils.py:122-157` | ok | def build_instrument_context( |
| tradingagents | N2 | dropped | `tradingagents/agents/utils/agent_utils.py:172-187` | ok | def get_instrument_context_from_state(state: Mapping[str, Any]) -> str: |
| tradingagents | N2 | dropped | `tradingagents/agents/utils/agent_utils.py:204-211` | ok | instrument_context = get_instrument_context_from_state(state) |
| tradingagents | N3 | run_attenuated | `tradingagents/agents/analysts/news_analyst.py:59-67` | ok | report = "" |
| finagent | N1 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html` | ok |  |
| finagent | N2 | dropped | `res/prompts/module/trading/decision_task_description_trading.html` | ok |  |
| finagent | N2 | dropped | `res/prompts/module/trading/market_intelligence_task_description_trading.html` | ok |  |
| finagent | N2 | dropped | `res/prompts/asset_infos/exp_stocks.json` | ok |  |
| finagent | N3 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html` | ok |  |
| finagent | - | - | `finagent/provider/provider.py:270-284` | ok | base64_image = encode_image(image_path) |
| finagent | - | - | `finagent/provider/provider.py:411-444` | ok | encoded_images = [encode_image(image_path) for image_path in image_filenames] |

## docs/applicability-matrix-material.json

| engine | class | verdict | citation | status | first cited line |
|---|---|---|---|---|---|
| finmem | - | - | `puppy/reflection.py:322-328` | ok | if short_memory: |
| finmem | - | - | `puppy/agent.py:33-34` | ok | if "gpt" in self.tokenization_model_name: |
| finmem | - | - | `puppy/agent.py:193` | ok | if self.model_name.startswith("tgi"): |
| finmem | - | - | `puppy/reflection.py:424-426` | ok | guard = gd.Guard.from_pydantic( |
| finmem | - | - | `puppy/reflection.py:227-243` | ok | def _add_momentum_info(momentum: int, investment_info: str) -> str: |
| finmem | - | - | `puppy/reflection.py:347-349` | ok | if momentum: |
| finmem | - | - | `puppy/portfolio.py:88-110` | ok | def get_moment(self, moment_window: int = 3) -> Union[Dict[str, int], None]: |
| finmem | - | - | `puppy/agent.py:188-192` | ok | cur_short_queried, cur_short_memory_id = self.brain.query_short( |
| finmem | - | - | `puppy/agent.py:189` | ok | query_text=self.character_string, |
| finmem | - | - | `puppy/memorydb.py:138-218` | wide | def query( |
| finmem | - | - | `puppy/memorydb.py:96-98` | ok | importance_scores = [ |
| finmem | - | - | `puppy/memory_functions/importance_score.py:31-35` | ok | class I_SampleInitialization_Short(ImportanceScoreInitialization): |
| finmem | - | - | `harness/build_corpus.py:58` | ok | DECISION_NEWS_ITEMS = 1 |
| finmem | - | - | `harness/corpus_config.json` | ok |  |
| finmem | - | - | `puppy/reflection.py:162-188` | ok | if (short_memory is None) or len(short_memory) == 0: |
| finmem | - | - | `puppy/prompts.py:17-24` | ok | test_sentiment_explanation = """For example, positive news about a company can lift investor sentim… |
| finmem | - | - | `puppy/prompts.py:16` | ok | test_investment_info_prefix = "The ticker of the stock to be analyzed is {symbol} and the current d… |
| finmem | - | - | `puppy/agent.py:404-419` | ok | reflection_result = trading_reflection( |
| finmem | - | - | `puppy/agent.py:587-590` | ok | self.portfolio.update_market_info( |
| finmem | - | - | `harness/build_corpus.py:97-98` | ok | "filing_k": {symbol: filing_k} if filing_k else {}, |
| finmem | M1 | run | `harness/build_corpus.py:195-200` | ok | def build_decision_corpus( |
| finmem | M1 | run | `harness/build_corpus.py:72-100` | ok | def day_record( |
| finmem | M1 | run | `puppy/reflection.py:325` | ok | [f"{i[0]}. {i[1].strip()}" for i in zip(short_memory_id, short_memory)] |
| finmem | M1 | run | `puppy/portfolio.py:88-110` | ok | def get_moment(self, moment_window: int = 3) -> Union[Dict[str, int], None]: |
| finmem | M1 | run | `harness/build_corpus.py:97-98` | ok | "filing_k": {symbol: filing_k} if filing_k else {}, |
| finmem | M1 | run | `config/tsla_gpt_config.toml:22` | ok | From year 2021 to 2022 September, Tesla's continued growth and solid financial performance over the… |
| finmem | M1 | run | `puppy/agent.py:404-419` | ok | reflection_result = trading_reflection( |
| finmem | M1 | run | `puppy/prompts.py:46-47` | ok | You should provide exactly one of the following investment decisions: buy or sell. |
| finmem | M1 | run | `puppy/reflection.py:108-112` | ok | investment_decision: str = Field( |
| finmem | M2 | run | `puppy/reflection.py:322-328` | ok | if short_memory: |
| finmem | M2 | run | `puppy/prompts.py:41-53` | ok | test_prompt = """ Given the information, can you make an investment decision? Just summarize the re… |
| finmem | M3 | run | `puppy/reflection.py:227-243` | ok | def _add_momentum_info(momentum: int, investment_info: str) -> str: |
| finmem | M3 | run | `puppy/portfolio.py:92-110` | ok | temp = np.cumsum((np.diff(self.market_price_series))[-moment_window:])[-1] |
| finmem | M3 | run | `puppy/reflection.py:347` | ok | if momentum: |
| finmem | M3 | run | `harness/corpus_config.json` | ok |  |
| finmem | M4 | no_target | `puppy/prompts.py:41-53` | ok | test_prompt = """ Given the information, can you make an investment decision? Just summarize the re… |
| finmem | M4 | no_target | `puppy/prompts.py:44` | ok | When cumulative return is positive or zero, you are a risk-seeking investor. |
| finmem | M4 | no_target | `config/tsla_gpt_config.toml:12-23` | ok | character_string = ''' |
| finmem | M4 | no_target | `puppy/agent.py:189` | ok | query_text=self.character_string, |
| finmem | M4 | no_target | `puppy/agent.py:404-419` | ok | reflection_result = trading_reflection( |
| finmem | M4 | no_target | `puppy/reflection.py:107-136` | ok | class InvestInfo(BaseModel): |
| finmem | M4 | no_target | `puppy/agent.py:421-426` | ok | if (reflection_result is not {}) and ("summary_reason" in reflection_result): |
| finmem | M5 | run | `puppy/reflection.py:325` | ok | [f"{i[0]}. {i[1].strip()}" for i in zip(short_memory_id, short_memory)] |
| finmem | M5 | run | `puppy/portfolio.py:94-110` | ok | if temp > 0: |
| finmem | M5 | run | `puppy/reflection.py:227-243` | ok | def _add_momentum_info(momentum: int, investment_info: str) -> str: |
| finmem | - | - | `harness/build_corpus.py:254-273` | ok | def check_numbers_preserved(base_text: str, variant: Dict[str, Any]) -> None: |
| finmem | - | - | `puppy/agent.py:208-209` | ok | for cur_id, cur_memory in zip(cur_short_memory_id, cur_short_queried): |
| finmem | - | - | `harness/build_corpus.py:343-359` | ok | excluded = list(config.get("excluded_klasses", [])) |
| finmem | - | - | `data-pipeline/05-get_sentiment_by_ticker.py:86-88` | ok | pos_sentence = f"The positive score for this news is {pos_score}." |
| finmem | - | - | `puppy/reflection.py:447` | ok | return {"investment_decision" : "hold", "summary_reason": validated_outcomes.__dict__['reask'].__di… |
| tradingagents | - | - | `tradingagents/agents/managers/portfolio_manager.py:56-61` | ok | **Context:** |
| tradingagents | - | - | `tradingagents/agents/risk_mgmt/aggressive_debator.py:30-35` | ok | {instrument_context} |
| tradingagents | - | - | `tradingagents/agents/managers/research_manager.py:43-44` | ok | **Debate History:** |
| tradingagents | - | - | `tradingagents/agents/trader/trader.py:43-48` | ok | f"Based on a comprehensive analysis by a team of analysts, here is an investment " |
| tradingagents | - | - | `tradingagents/graph/setup.py:62` | ok | self, selected_analysts=("market", "social", "news", "fundamentals") |
| tradingagents | - | - | `tradingagents/graph/analyst_execution.py:28-38` | ok | "social": AnalystNodeSpec( |
| tradingagents | - | - | `tradingagents/agents/analysts/social_media_analyst.py:1-9` | ok | """Backwards-compatibility shim for the renamed module. |
| tradingagents | - | - | `tradingagents/agents/analysts/news_analyst.py:20-28` | ok | tools = [ |
| tradingagents | - | - | `tradingagents/agents/utils/news_data_tools.py:24` | ok | return route_to_vendor("get_news", ticker, start_date, end_date) |
| tradingagents | - | - | `tradingagents/agents/analysts/sentiment_analyst.py:70` | ok | news_block = get_news.func(ticker, start_date, end_date) |
| tradingagents | - | - | `tradingagents/agents/analysts/sentiment_analyst.py:47-48` | ok | def _seven_days_back(trade_date: str) -> str: |
| tradingagents | - | - | `tradingagents/agents/analysts/sentiment_analyst.py:136-146` | ok | return f"""You are a financial market sentiment analyst. Your task is to produce a comprehensive se… |
| tradingagents | - | - | `tradingagents/agents/utils/core_stock_tools.py:24` | ok | return route_to_vendor("get_stock_data", symbol, start_date, end_date) |
| tradingagents | - | - | `tradingagents/dataflows/y_finance.py:18-70` | wide | def get_YFin_data_online( |
| tradingagents | - | - | `tradingagents/agents/utils/market_data_validation_tools.py:5` | ok | from tradingagents.dataflows.market_data_validator import build_verified_market_snapshot |
| tradingagents | - | - | `tradingagents/dataflows/market_data_validator.py:1-8` | ok | """Deterministic market-data verification snapshot. |
| tradingagents | - | - | `tradingagents/agents/analysts/fundamentals_analyst.py:18-28` | ok | tools = [ |
| tradingagents | - | - | `tradingagents/dataflows/y_finance.py:296-297` | ok | ("EPS (TTM)", info.get("trailingEps")), |
| tradingagents | - | - | `tradingagents/dataflows/y_finance.py:304` | ok | ("Revenue (TTM)", info.get("totalRevenue")), |
| tradingagents | - | - | `tradingagents/dataflows/y_finance.py:276` | ok | curr_date: Annotated[str, "current date (not used for yfinance)"] = None |
| tradingagents | - | - | `tradingagents/dataflows/y_finance.py:421-426` | ok | if freq.lower() == "quarterly": |
| tradingagents | - | - | `tradingagents/dataflows/stockstats_utils.py:224-235` | ok | def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame: |
| tradingagents | - | - | `tradingagents/agents/analysts/sentiment_analyst.py:43-44` | ok | from tradingagents.dataflows.reddit import fetch_reddit_posts |
| tradingagents | - | - | `tradingagents/agents/analysts/sentiment_analyst.py:71-72` | ok | stocktwits_block = fetch_stocktwits_messages(ticker, limit=30) |
| tradingagents | - | - | `tradingagents/dataflows/stocktwits.py:41` | ok | def fetch_stocktwits_messages(ticker: str, limit: int = 30, timeout: float = 10.0) -> str: |
| tradingagents | - | - | `tradingagents/dataflows/stocktwits.py:58` | ok | return f"<stocktwits unavailable: {type(exc).__name__}>" |
| tradingagents | - | - | `tradingagents/dataflows/reddit.py:191` | ok | def fetch_reddit_posts( |
| tradingagents | - | - | `tradingagents/graph/trading_graph.py:423` | ok | past_context = self.memory_log.get_past_context(company_name) |
| tradingagents | - | - | `tradingagents/agents/utils/memory.py:70-95` | ok | def get_past_context(self, ticker: str, n_same: int = 5, n_cross: int = 3) -> str: |
| tradingagents | - | - | `tradingagents/agents/managers/portfolio_manager.py:36-41` | ok | past_context = state.get("past_context", "") |
| tradingagents | - | - | `tradingagents/graph/trading_graph.py:296-334` | ok | def _resolve_pending_entries(self, ticker: str) -> None: |
| tradingagents | - | - | `tradingagents/default_config.py:75` | ok | "memory_log_path": os.getenv("TRADINGAGENTS_MEMORY_LOG_PATH", os.path.join(_TRADINGAGENTS_HOME, "me… |
| tradingagents | - | - | `tradingagents/agents/utils/agent_utils.py:122-169` | wide | def build_instrument_context( |
| tradingagents | - | - | `tradingagents/agents/utils/agent_utils.py:78-99` | ok | @functools.lru_cache(maxsize=256) |
| tradingagents | M1 | dropped | `tradingagents/graph/setup.py:62` | ok | self, selected_analysts=("market", "social", "news", "fundamentals") |
| tradingagents | M1 | dropped | `tradingagents/agents/analysts/fundamentals_analyst.py:18-28` | ok | tools = [ |
| tradingagents | M1 | dropped | `tradingagents/default_config.py:136` | ok | "fundamental_data": "yfinance",      # Options: alpha_vantage, yfinance |
| tradingagents | M1 | dropped | `tradingagents/dataflows/y_finance.py:296-297` | ok | ("EPS (TTM)", info.get("trailingEps")), |
| tradingagents | M1 | dropped | `tradingagents/dataflows/y_finance.py:304` | ok | ("Revenue (TTM)", info.get("totalRevenue")), |
| tradingagents | M1 | dropped | `tradingagents/dataflows/y_finance.py:276` | ok | curr_date: Annotated[str, "current date (not used for yfinance)"] = None |
| tradingagents | M1 | dropped | `tradingagents/dataflows/y_finance.py:421-426` | ok | if freq.lower() == "quarterly": |
| tradingagents | M1 | dropped | `tradingagents/dataflows/y_finance.py:432` | ok | csv_string = data.to_csv() |
| tradingagents | M1 | dropped | `tradingagents/dataflows/stockstats_utils.py:224-235` | ok | def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame: |
| tradingagents | M1 | dropped | `tradingagents/dataflows/alpha_vantage_fundamentals.py:30-63` | ok | def get_fundamentals(ticker: str, curr_date: str = None) -> str: |
| tradingagents | M1 | dropped | `tradingagents/agents/researchers/bull_researcher.py:41` | ok | {fundamentals_label}: {fundamentals_report} |
| tradingagents | M1 | dropped | `tradingagents/agents/risk_mgmt/aggressive_debator.py:34` | ok | Company Fundamentals Report: {fundamentals_report} |
| tradingagents | M2 | dropped | `tradingagents/dataflows/y_finance.py:421-438` | ok | if freq.lower() == "quarterly": |
| tradingagents | M2 | dropped | `tradingagents/dataflows/stockstats_utils.py:224-235` | ok | def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame: |
| tradingagents | M2 | dropped | `tradingagents/agents/researchers/bear_researcher.py:43` | ok | {fundamentals_label}: {fundamentals_report} |
| tradingagents | M2 | dropped | `tradingagents/agents/risk_mgmt/conservative_debator.py:34` | ok | Company Fundamentals Report: {fundamentals_report} |
| tradingagents | M2 | dropped | `tradingagents/agents/risk_mgmt/neutral_debator.py:34` | ok | Company Fundamentals Report: {fundamentals_report} |
| tradingagents | M3 | run_attenuated | `tradingagents/agents/analysts/sentiment_analyst.py:70` | ok | news_block = get_news.func(ticker, start_date, end_date) |
| tradingagents | M3 | run_attenuated | `tradingagents/agents/schemas.py:258-303` | wide | class SentimentBand(str, Enum): |
| tradingagents | M3 | run_attenuated | `tradingagents/agents/analysts/news_analyst.py:59-67` | ok | report = "" |
| tradingagents | M3 | run_attenuated | `tradingagents/dataflows/y_finance.py:54-70` | ok | # Round numerical values to 2 decimal places for cleaner display |
| tradingagents | M3 | run_attenuated | `tradingagents/dataflows/market_data_validator.py:1-8` | ok | """Deterministic market-data verification snapshot. |
| tradingagents | M3 | run_attenuated | `tradingagents/dataflows/y_finance.py:297` | ok | ("Forward EPS", info.get("forwardEps")), |
| tradingagents | M4 | no_target | `tradingagents/agents/analysts/market_analyst.py:25-53` | ok | """You are a trading assistant tasked with analyzing financial markets. Your role is to select the … |
| tradingagents | M4 | no_target | `tradingagents/agents/schemas.py:139-147` | ok | entry_price: float \| None = Field( |
| tradingagents | M4 | no_target | `tradingagents/agents/schemas.py:216-219` | ok | price_target: float \| None = Field( |
| tradingagents | M4 | no_target | `tradingagents/agents/schemas.py:44-51` | ok | class PortfolioRating(str, Enum): |
| tradingagents | M4 | no_target | `tradingagents/graph/reflection.py:20-29` | ok | return ( |
| tradingagents | M4 | no_target | `tradingagents/agents/managers/portfolio_manager.py:36-41` | ok | past_context = state.get("past_context", "") |
| tradingagents | M4 | no_target | `tradingagents/agents/schemas.py:211-213` | ok | "Detailed reasoning anchored in specific evidence from the analysts' " |
| tradingagents | M4 | no_target | `tradingagents/default_config.py:75` | ok | "memory_log_path": os.getenv("TRADINGAGENTS_MEMORY_LOG_PATH", os.path.join(_TRADINGAGENTS_HOME, "me… |
| tradingagents | M5 | run_attenuated | `tradingagents/dataflows/y_finance.py:54-70` | ok | # Round numerical values to 2 decimal places for cleaner display |
| tradingagents | M5 | run_attenuated | `tradingagents/dataflows/market_data_validator.py:1-8` | ok | """Deterministic market-data verification snapshot. |
| tradingagents | M5 | run_attenuated | `tradingagents/dataflows/y_finance.py:421-426` | ok | if freq.lower() == "quarterly": |
| tradingagents | M5 | run_attenuated | `tradingagents/agents/analysts/news_analyst.py:59-67` | ok | report = "" |
| tradingagents | M5 | run_attenuated | `tradingagents/agents/analysts/sentiment_analyst.py:70` | ok | news_block = get_news.func(ticker, start_date, end_date) |
| tradingagents | - | - | `tradingagents/dataflows/market_data_validator.py:35` | ok | data = load_ohlcv(symbol, curr_date) |
| tradingagents | - | - | `tradingagents/dataflows/stockstats_utils.py:148-175` | ok | def load_ohlcv(symbol: str, curr_date: str) -> pd.DataFrame: |
| tradingagents | - | - | `tradingagents/agents/schemas.py:44-51` | ok | class PortfolioRating(str, Enum): |
| tradingagents | - | - | `tradingagents/agents/utils/rating.py:28-48` | ok | def parse_rating(text: str, default: str = "Hold") -> str: |
| tradingagents | - | - | `tradingagents/agents/utils/rating.py:48` | ok | return default |
| tradingagents | - | - | `tradingagents/default_config.py:110-111` | ok | "max_debate_rounds": 1, |
| finagent | - | - | `finagent/prompt/trading/latest_market_intelligence_summary.py:72-80` | ok | for row in news.iterrows(): |
| finagent | - | - | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:8-9` | ok | <br> - Analyze the market sentiment and provide the type of market sentiment. A clear preference ov… |
| finagent | - | - | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:19` | ok | <br>4. You should provide an overall analysis of all the market intelligence, explicitly provide a … |
| finagent | - | - | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:21` | ok | <br>6. The summary you provide should be concise and clear, with no more than 300 tokens. |
| finagent | - | - | `res/prompts/template/valid/trading/decision.html:21` | ok | <br>$$latest_market_intelligence_summary$$ |
| finagent | - | - | `res/prompts/template/valid/trading/low_level_reflection.html:16-21` | ok | <p class="placeholder">The following are summaries of the latest (i.e., today) and past (i.e., befo… |
| finagent | - | - | `res/prompts/template/valid/trading/high_level_reflection.html:14-21` | ok | <div class="market_intelligence"> |
| finagent | - | - | `tools/main.py` | ok |  |
| finagent | - | - | `finagent/environment/trading.py:121-125` | ok | days_ago = self.prices_df.index[self.day - self.look_back_days] |
| finagent | - | - | `configs/exp/trading/TSLA.py:25-26` | ok | look_forward_days = long_term_next_date_range |
| finagent | - | - | `finagent/plots/kline.py:32-33` | ok | if not mode == "train": |
| finagent | - | - | `tools/main.py:232` | ok | kline_path = plots.plot_kline(state=state, info=info, save_dir=save_dir) |
| finagent | - | - | `finagent/plots/interface.py:31` | ok | def plot_kline(self, state, info, save_dir, mode = "train"): |
| finagent | - | - | `finagent/plots/interface.py:59` | ok | mode=mode) |
| finagent | - | - | `tools/main_mi_w_low_w_high_w_tool_w_decision.py:231` | ok | kline_path = plots.plot_kline(state=state, info=info, save_dir=save_dir, mode=mode) |
| finagent | - | - | `finagent/environment/trading.py:122` | ok | days_future = self.prices_df.index[min(self.day + self.look_forward_days, len(self.prices_df) - 1)] |
| finagent | - | - | `configs/exp/trading/TSLA.py:36-40` | ok | valid_latest_market_intelligence_summary_template_path = "res/prompts/template/valid/trading/latest… |
| finagent | - | - | `configs/exp/trading_mi_w_low_w_high_w_tool_w_decision/TSLA.py:40` | ok | valid_decision_template_path = "res/prompts/template/valid/trading_mi-w-low-w-high-w-decision/decis… |
| finagent | - | - | `configs/exp/trading_only_strategy_with_record/TSLA_only_strategy.py:40` | ok | valid_decision_template_path = "res/prompts/template/valid/only_strategy_trading/decision_with_reco… |
| finagent | - | - | `res/prompts/template/valid/trading_mi-w-low-w-high-w-tool-w-decision/decision.html:50-52` | ok | <iframe name="decision_guidance_trading"></iframe> |
| finagent | - | - | `res/prompts/module/trading/decision_task_description_trading.html:2` | ok | <p class="placeholder">You are currently targeting the trading of a company known as $$asset_name$$… |
| finagent | - | - | `res/prompts/asset_infos/exp_stocks.json` | ok |  |
| finagent | - | - | `finagent/prompt/trading/latest_market_intelligence_summary.py:57-63` | ok | if len(price) > 0: |
| finagent | - | - | `res/prompts/module/trading/low_level_reflection_kline_chart_trading.html:2-15` | ok | <p class="text">The following is a Kline chart with Moving Average (MA) and Bollinger Bands (BB) te… |
| finagent | - | - | `finagent/plots/interface.py:31-64` | ok | def plot_kline(self, state, info, save_dir, mode = "train"): |
| finagent | - | - | `finagent/prompt/trading/low_level_reflection.py:60-68` | ok | past_price = price[price["timestamp"] <= current_date] |
| finagent | - | - | `res/prompts/module/trading/low_level_reflection_price_change_description_trading.html:3-5` | ok | <br>1. Short-Term: Over the past $$short_term_past_date_range$$ days, the price movement ratio has … |
| finagent | - | - | `res/prompts/module/trading/high_level_reflection_trading_chart_trading.html:2-13` | ok | <p class="placeholder">The following figure showing the Adj Close price movements with trading deci… |
| finagent | - | - | `res/prompts/module/trading/decision_state_description_trading.html:2` | ok | <p class="placeholder">For the current situation, the Adj Close price of the asset is $$asset_price… |
| finagent | - | - | `finagent/prompt/trading/decision.py:42-52` | ok | asset_price = info["price"] |
| finagent | - | - | `finagent/prompt/helper.py:248-321` | wide | def prepare_latest_market_intelligence_params(state: Dict, |
| finagent | - | - | `finagent/prompt/trading/latest_market_intelligence_summary.py:167-176` | ok | data = { |
| finagent | - | - | `res/prompts/trader/*.txt` | ok |  |
| finagent | - | - | `res/prompts/trader/*.txt` | ok |  |
| finagent | - | - | `res/prompts/trader/*.txt` | ok |  |
| finagent | - | - | `res/prompts/trader/*.txt` | ok |  |
| finagent | - | - | `res/prompts/trader/*.txt` | ok |  |
| finagent | - | - | `res/prompts/trader/*.txt` | ok |  |
| finagent | - | - | `tools/main.py:371` | ok | trader_preference = ASSET.get_trader(cfg.trader_preference) |
| finagent | - | - | `finagent/provider/provider.py:270-284` | ok | base64_image = encode_image(image_path) |
| finagent | - | - | `finagent/provider/provider.py:411-444` | ok | encoded_images = [encode_image(image_path) for image_path in image_filenames] |
| finagent | - | - | `finagent/prompt/custom.py:81-96` | ok | elif tag.name == "img": |
| finagent | - | - | `finagent/data/dataset.py:53` | ok | self.news = self._load_news() |
| finagent | - | - | `finagent/environment/trading.py:31-35` | ok | self.prices = self.dataset.prices |
| finagent | M1 | run_attenuated | `finagent/prompt/trading/latest_market_intelligence_summary.py:72-80` | ok | for row in news.iterrows(): |
| finagent | M1 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:8` | ok | <br> - Analyze the market sentiment and provide the type of market sentiment. A clear preference ov… |
| finagent | M1 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:9` | ok | <br>3. The analysis you provide for each piece of market intelligence should be concise and clear, … |
| finagent | M1 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:21` | ok | <br>6. The summary you provide should be concise and clear, with no more than 300 tokens. |
| finagent | M1 | run_attenuated | `finagent/prompt/trading/latest_market_intelligence_summary.py:57-63` | ok | if len(price) > 0: |
| finagent | M1 | run_attenuated | `finagent/data/dataset.py:53` | ok | self.news = self._load_news() |
| finagent | M1 | run_attenuated | `res/prompts/template/valid/trading/decision.html:21` | ok | <br>$$latest_market_intelligence_summary$$ |
| finagent | M1 | run_attenuated | `res/prompts/module/trading/decision_prompt_trading.html:8-9` | ok | <br> - If the future trend is bullish, you should consider a BUY instead of a HOLD to increase your… |
| finagent | M2 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:9` | ok | <br>3. The analysis you provide for each piece of market intelligence should be concise and clear, … |
| finagent | M2 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:19` | ok | <br>4. You should provide an overall analysis of all the market intelligence, explicitly provide a … |
| finagent | M2 | run_attenuated | `res/prompts/module/trading/decision_prompt_trading.html:5` | ok | <br> - If the overall is neurtal, your decision should pay less attention to the summary of market … |
| finagent | M2 | run_attenuated | `res/prompts/template/valid/trading/decision.html:21` | ok | <br>$$latest_market_intelligence_summary$$ |
| finagent | M3 | run_attenuated | `finagent/prompt/trading/latest_market_intelligence_summary.py:57-63` | ok | if len(price) > 0: |
| finagent | M3 | run_attenuated | `res/prompts/module/trading/low_level_reflection_kline_chart_trading.html:2-15` | ok | <p class="text">The following is a Kline chart with Moving Average (MA) and Bollinger Bands (BB) te… |
| finagent | M3 | run_attenuated | `finagent/prompt/trading/low_level_reflection.py:63-68` | ok | short_term_past_price_movement = past_price["adj_close"].pct_change(periods=self.short_term_past_da… |
| finagent | M3 | run_attenuated | `res/prompts/module/trading/low_level_reflection_price_change_description_trading.html:3-5` | ok | <br>1. Short-Term: Over the past $$short_term_past_date_range$$ days, the price movement ratio has … |
| finagent | M3 | run_attenuated | `finagent/data/dataset.py:53` | ok | self.news = self._load_news() |
| finagent | M4 | no_target | `res/prompts/module/trading/decision_strategy_trading.html:3` | ok | <br><br> 1. MACD Crossover Strategy - This strategy generates buy signals when the MACD line crosse… |
| finagent | M4 | no_target | `res/prompts/module/trading/decision_strategy_trading.html:5` | ok | <br><br> 2. KDJ with RSI Filter Strategy - This strategy works best in sideways or ranging markets,… |
| finagent | M4 | no_target | `res/prompts/module/trading/decision_strategy_trading.html:7` | ok | <br><br> 3. Stochastic Oscillator and Bollinger Bands Strategy - This strategy is effective in mark… |
| finagent | M4 | no_target | `res/prompts/module/trading/decision_strategy_trading.html:9` | ok | <br><br> 4. Mean Reversion Strategy - This strategy assumes that prices will revert to their mean o… |
| finagent | M4 | no_target | `res/prompts/module/trading/decision_strategy_trading_with_record.html:6-17` | ok | <br><br> 1. MACD Crossover Strategy - This strategy generates buy signals when the MACD line crosse… |
| finagent | M4 | no_target | `finagent/tools/strategy_agents.py:86` | ok | [Description] : This strategy uses the Moving Average Convergence Divergence (MACD) indicator to ge… |
| finagent | M4 | no_target | `finagent/tools/strategy_agents.py:118` | ok | [Short Description] : This strategy uses the KDJ (Stochastic Oscillator) and RSI (Relative Strength… |
| finagent | M4 | no_target | `finagent/tools/strategy_agents.py:158` | ok | [Description] : This strategy combines the StochasticVMA Oscillator and Bollinger Bands to generate… |
| finagent | M4 | no_target | `finagent/tools/strategy_agents.py:206` | ok | [Description] : This strategy assumes that the price will revert to its mean over time. A BUY signa… |
| finagent | M4 | no_target | `configs/exp/trading_only_strategy_with_record/TSLA_only_strategy.py:40` | ok | valid_decision_template_path = "res/prompts/template/valid/only_strategy_trading/decision_with_reco… |
| finagent | M4 | no_target | `res/prompts/template/valid/only_strategy_trading/decision_with_record.html:11-25` | ok | <div class="message" role="user"> |
| finagent | M4 | no_target | `configs/exp/trading/TSLA.py:40` | ok | valid_decision_template_path = "res/prompts/template/valid/trading/decision.html" |
| finagent | M4 | no_target | `configs/exp/trading_mi_w_low_w_high_w_tool_w_decision/TSLA.py:40` | ok | valid_decision_template_path = "res/prompts/template/valid/trading_mi-w-low-w-high-w-decision/decis… |
| finagent | M4 | no_target | `tools/main.py:32-41` | ok | parser.add_argument( |
| finagent | M4 | no_target | `finagent/prompt/helper.py:155-188` | ok | for i in range(4): |
| finagent | M4 | no_target | `res/prompts/module/trading/decision_output_format_trading.html:5` | ok | <br>&#9;&lt;string name="action"&gt;BUY&lt;/string&gt; |
| finagent | M5 | run_attenuated | `finagent/prompt/trading/low_level_reflection.py:63-68` | ok | short_term_past_price_movement = past_price["adj_close"].pct_change(periods=self.short_term_past_da… |
| finagent | M5 | run_attenuated | `res/prompts/module/trading/low_level_reflection_price_change_description_trading.html:3-5` | ok | <br>1. Short-Term: Over the past $$short_term_past_date_range$$ days, the price movement ratio has … |
| finagent | M5 | run_attenuated | `finagent/data/dataset.py:53` | ok | self.news = self._load_news() |
| finagent | M5 | run_attenuated | `res/prompts/module/trading/market_intelligence_latest_summary_prompt_trading.html:21` | ok | <br>6. The summary you provide should be concise and clear, with no more than 300 tokens. |
| finagent | - | - | `finagent/environment/trading.py:199-229` | ok | def buy(self, price, amount=1): |
| finagent | - | - | `tools/main.py:208-209` | ok | if trading_records["action"][-1] != info["action"]: |
| finagent | - | - | `tools/main.py:404` | ok | trading_records["action"].append(decision_res["response_dict"]["action"]) |
| finagent | - | - | `tools/main.py:407` | ok | action = decision_res["response_dict"]["action"] |
| finagent | - | - | `res/prompts/template/valid/trading_mi-w-low-w-high-w-tool-w-decision/decision.html:74` | ok | <br>9. Before making a decision, you must check the current situation. If your CASH reserve is lowe… |
| finagent | - | - | `finagent/prompt/trading/latest_market_intelligence_summary.py:52-53` | ok | if len(news) > 20: |
| cross-cutting | price_path_never_the_perturbed_content | - | `puppy/reflection.py:227-243` | ok | def _add_momentum_info(momentum: int, investment_info: str) -> str: |
| cross-cutting | price_path_never_the_perturbed_content | - | `finagent/prompt/trading/low_level_reflection.py:60-68` | ok | past_price = price[price["timestamp"] <= current_date] |
| cross-cutting | harness_prerequisites | - | `harness/build_corpus.py:254-273` | ok | def check_numbers_preserved(base_text: str, variant: Dict[str, Any]) -> None: |
| cross-cutting | harness_prerequisites | - | `puppy/agent.py:208-209` | ok | for cur_id, cur_memory in zip(cur_short_memory_id, cur_short_queried): |

**Summary:** 241 citations — ok 234, wide 5, external 2. Result: PASS.

## External references (not verifiable by this script)

| matrix | engine | class | reference |
|---|---|---|---|
| docs/applicability-matrix.json | tradingagents | N2 | #814 |
| docs/applicability-matrix-material.json | finagent | - | #2 |
