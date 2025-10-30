#!/usr/bin/env python3
"""
ReBrowser Playwright Tool - Direct Playwright browser automation with stealth
Replaces AWS AgentCoreBrowser with local ReBrowser-Playwright
"""

import asyncio
import logging
import random
import math
import nest_asyncio
from typing import Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field
from strands import tool
from rebrowser_playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Allow nested event loops (needed for Strands integration)
nest_asyncio.apply()

logger = logging.getLogger(__name__)


class BrowserSession:
    """Browser session management"""
    def __init__(self, session_name: str, description: str, browser: Browser, context: BrowserContext, page: Page):
        self.session_name = session_name
        self.description = description
        self.browser = browser
        self.context = context
        self.page = page
        self.tabs: Dict[str, Page] = {"main": page}
        self.active_tab_id = "main"

    def get_active_page(self) -> Page:
        return self.tabs[self.active_tab_id]

    def add_tab(self, tab_id: str, page: Page):
        self.tabs[tab_id] = page

    def set_active_tab(self, tab_id: str):
        if tab_id in self.tabs:
            self.active_tab_id = tab_id


# Action Models
class InitSessionAction(BaseModel):
    type: Literal["init_session"] = "init_session"
    session_name: str
    description: Optional[str] = "Browser session"


class NavigateAction(BaseModel):
    type: Literal["navigate"] = "navigate"
    url: str
    session_name: str
    description: Optional[str] = "Navigate to URL"


class ClickAction(BaseModel):
    type: Literal["click"] = "click"
    selector: str
    session_name: str
    description: Optional[str] = "Click element"


class ClickCoordinateAction(BaseModel):
    type: Literal["click_coordinate"] = "click_coordinate"
    x: int
    y: int
    session_name: str
    description: Optional[str] = "Click at coordinates"


class TypeAction(BaseModel):
    type: Literal["type"] = "type"
    selector: str
    text: str
    session_name: str
    description: Optional[str] = "Type text"


class TypeWithKeyboardAction(BaseModel):
    type: Literal["type_with_keyboard"] = "type_with_keyboard"
    text: str
    session_name: str
    description: Optional[str] = "Type with keyboard"


class PressDeleteAction(BaseModel):
    type: Literal["press_delete"] = "press_delete"
    times: int
    session_name: str
    description: Optional[str] = "Press delete key multiple times"


class HumanMouseAction(BaseModel):
    type: Literal["human_mouse_move"] = "human_mouse_move"
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    session_name: str
    description: Optional[str] = "Human-like mouse movement"


class PressAndHoldAction(BaseModel):
    type: Literal["press_and_hold"] = "press_and_hold"
    hold_time: float
    session_name: str
    description: Optional[str] = "Press and hold mouse"


class ScreenshotAction(BaseModel):
    type: Literal["screenshot"] = "screenshot"
    session_name: str
    description: Optional[str] = "Take screenshot"


class GetTextAction(BaseModel):
    type: Literal["get_text"] = "get_text"
    selector: str
    session_name: str
    description: Optional[str] = "Get element text"


class GetHtmlAction(BaseModel):
    type: Literal["get_html"] = "get_html"
    session_name: str
    description: Optional[str] = "Get page HTML"


class EvaluateAction(BaseModel):
    type: Literal["evaluate"] = "evaluate"
    script: str
    session_name: str
    description: Optional[str] = "Execute JavaScript"


class WaitAction(BaseModel):
    type: Literal["wait"] = "wait"
    timeout: int
    session_name: str
    description: Optional[str] = "Wait"


class NewTabAction(BaseModel):
    type: Literal["new_tab"] = "new_tab"
    session_name: str
    description: Optional[str] = "Open new tab"


class SwitchTabAction(BaseModel):
    type: Literal["switch_tab"] = "switch_tab"
    tab_id: str
    session_name: str
    description: Optional[str] = "Switch tab"


class ListTabsAction(BaseModel):
    type: Literal["list_tabs"] = "list_tabs"
    session_name: str
    description: Optional[str] = "List tabs"


class CloseAction(BaseModel):
    type: Literal["close"] = "close"
    session_name: str
    description: Optional[str] = "Close session"


class BrowserInput(BaseModel):
    action: Union[
        InitSessionAction,
        NavigateAction,
        ClickAction,
        ClickCoordinateAction,
        TypeAction,
        TypeWithKeyboardAction,
        PressDeleteAction,
        HumanMouseAction,
        PressAndHoldAction,
        ScreenshotAction,
        GetTextAction,
        GetHtmlAction,
        EvaluateAction,
        WaitAction,
        NewTabAction,
        SwitchTabAction,
        ListTabsAction,
        CloseAction,
    ] = Field(discriminator="type")
    wait_time: Optional[int] = Field(default=2, description="Time to wait after action in seconds")


class ReBrowserPlaywrightTool:
    """ReBrowser Playwright browser automation tool with stealth capabilities"""

    def __init__(self):
        self._sessions: Dict[str, BrowserSession] = {}
        self._playwright = None
        self._started = False
        logger.info("ReBrowserPlaywrightTool initialized")

    async def _ensure_started(self):
        """Ensure Playwright is started"""
        if not self._started:
            self._playwright = await async_playwright().start()
            self._started = True
            logger.info("Playwright started")

    @tool
    def browser(self, browser_input: BrowserInput) -> Dict[str, Any]:
        """Browser automation tool with stealth capabilities"""
        if isinstance(browser_input, dict):
            action = BrowserInput.model_validate(browser_input).action
            wait_time = browser_input.get("wait_time", 2)
        else:
            action = browser_input.action
            wait_time = browser_input.wait_time

        # Route to appropriate handler
        handlers = {
            "init_session": self._async_init_session,
            "navigate": self._async_navigate,
            "click": self._async_click,
            "click_coordinate": self._async_click_coordinate,
            "type": self._async_type,
            "type_with_keyboard": self._async_type_with_keyboard,
            "press_delete": self._async_press_delete,
            "human_mouse_move": self._async_human_mouse_move,
            "press_and_hold": self._async_press_and_hold,
            "screenshot": self._async_screenshot,
            "get_text": self._async_get_text,
            "get_html": self._async_get_html,
            "evaluate": self._async_evaluate,
            "wait": self._async_wait,
            "new_tab": self._async_new_tab,
            "switch_tab": self._async_switch_tab,
            "list_tabs": self._async_list_tabs,
            "close": self._async_close,
        }

        handler = handlers.get(action.type)
        if not handler:
            return {"status": "error", "content": [{"text": f"Unknown action: {action.type}"}]}

        # Execute async handler
        result = asyncio.run(handler(action))

        # Wait after action
        if wait_time > 0:
            asyncio.run(asyncio.sleep(wait_time))

        return result

    async def _async_init_session(self, action: InitSessionAction) -> Dict[str, Any]:
        """Initialize browser session with stealth configuration"""
        logger.info(f"Initializing browser session: {action.description}")

        session_name = action.session_name
        if session_name in self._sessions:
            return {"status": "error", "content": [{"text": f"Session '{session_name}' already exists"}]}

        try:
            await self._ensure_started()

            # Launch browser with stealth args and fixed window size
            # Using headless mode with new Chrome headless (more undetectable)
            browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--window-size=1280,800',  # Fixed window size
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                ]
            )

            # Create context with matching fixed viewport for accurate coordinates
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},  # Must match window size
                screen={'width': 1280, 'height': 800},
                device_scale_factor=1.0,  # Force 1:1 pixel ratio for consistent screenshots
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            )

            # Create page
            page = await context.new_page()

            # Apply additional stealth JavaScript
            await page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });

                // Override platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Linux x86_64',
                    configurable: true
                });

                // Add chrome property
                window.chrome = {
                    runtime: {}
                };

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)

            # Create session
            session = BrowserSession(
                session_name=session_name,
                description=action.description,
                browser=browser,
                context=context,
                page=page
            )

            self._sessions[session_name] = session
            logger.info(f"Session '{session_name}' initialized successfully")

            return {
                "status": "success",
                "content": [{
                    "json": {
                        "sessionName": session_name,
                        "description": action.description
                    }
                }]
            }

        except Exception as e:
            logger.error(f"Failed to initialize session: {str(e)}")
            return {"status": "error", "content": [{"text": f"Failed to initialize session: {str(e)}"}]}

    async def _async_navigate(self, action: NavigateAction) -> Dict[str, Any]:
        """Navigate to URL"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            # Use timeout and don't wait for full load (some sites have anti-bot challenges)
            await page.goto(action.url, wait_until='commit', timeout=30000)
            logger.info(f"Navigated to {action.url}")

            # Wait a bit for page to render
            await asyncio.sleep(2)

            return {
                "status": "success",
                "content": [{
                    "json": {
                        "url": page.url,
                        "title": await page.title()
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Navigation failed: {str(e)}"}]}

    async def _async_click(self, action: ClickAction) -> Dict[str, Any]:
        """Click element by selector"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            await page.click(action.selector, timeout=15000)
            logger.info(f"Clicked element: {action.selector}")

            return {"status": "success", "content": [{"json": {"selector": action.selector}}]}
        except Exception as e:
            logger.error(f"Click failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Click failed: {str(e)}"}]}

    async def _async_click_coordinate(self, action: ClickCoordinateAction) -> Dict[str, Any]:
        """Click at specific coordinates using mouse.click"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()

            # Simple mouse click at coordinates (viewport must match window size)
            await page.mouse.click(action.x, action.y)
            logger.info(f"Clicked at ({action.x}, {action.y})")

            return {
                "status": "success",
                "content": [{
                    "json": {
                        "action": "click_coordinate",
                        "coordinates": {"x": action.x, "y": action.y}
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Coordinate click failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Coordinate click failed: {str(e)}"}]}

    async def _async_type(self, action: TypeAction) -> Dict[str, Any]:
        """Type text into element"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            await page.fill(action.selector, action.text, timeout=15000)
            logger.info(f"Typed into {action.selector}")

            return {"status": "success", "content": [{"json": {"selector": action.selector}}]}
        except Exception as e:
            logger.error(f"Type failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Type failed: {str(e)}"}]}

    async def _async_type_with_keyboard(self, action: TypeWithKeyboardAction) -> Dict[str, Any]:
        """Type text using keyboard (character by character)"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            for char in action.text:
                await page.keyboard.press(char)
                await asyncio.sleep(0.05)

            logger.info(f"Typed with keyboard: {action.text}")
            return {"status": "success", "content": [{"json": {"text": action.text}}]}
        except Exception as e:
            logger.error(f"Keyboard typing failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Keyboard typing failed: {str(e)}"}]}

    async def _async_press_delete(self, action: PressDeleteAction) -> Dict[str, Any]:
        """Press backspace key multiple times"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            for _ in range(action.times):
                await page.keyboard.press('Backspace')
                await asyncio.sleep(0.05)

            logger.info(f"Pressed Backspace {action.times} times")
            return {"status": "success", "content": [{"json": {"times": action.times}}]}
        except Exception as e:
            logger.error(f"Press delete failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Press delete failed: {str(e)}"}]}

    async def _async_human_mouse_move(self, action: HumanMouseAction) -> Dict[str, Any]:
        """Human-like mouse movement with curve"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()

            # Calculate movement with curve
            distance = math.sqrt((action.end_x - action.start_x)**2 + (action.end_y - action.start_y)**2)
            steps = max(8, int(distance / 10))

            # Create curve
            mid_x = (action.start_x + action.end_x) / 2
            mid_y = (action.start_y + action.end_y) / 2

            if distance > 5:
                angle = math.atan2(action.end_y - action.start_y, action.end_x - action.start_x)
                curve_offset = distance * 0.2 * random.uniform(0.3, 0.8)
                ctrl_x = mid_x + math.cos(angle + math.pi/2) * curve_offset
                ctrl_y = mid_y + math.sin(angle + math.pi/2) * curve_offset
            else:
                ctrl_x, ctrl_y = mid_x, mid_y

            # Move in steps (Bezier curve)
            for i in range(steps + 1):
                t = i / steps
                x = (1-t)**2 * action.start_x + 2*(1-t)*t * ctrl_x + t**2 * action.end_x
                y = (1-t)**2 * action.start_y + 2*(1-t)*t * ctrl_y + t**2 * action.end_y

                # Add jitter
                x += random.uniform(-0.5, 0.5)
                y += random.uniform(-0.5, 0.5)

                await page.mouse.move(int(x), int(y))

                # Variable speed
                speed_factor = 1 - abs(0.5 - t) * 0.4
                await asyncio.sleep(0.02 + speed_factor * 0.03)

            # Small pause and tremor
            await asyncio.sleep(random.uniform(0.1, 0.3))
            await page.mouse.move(
                action.end_x + random.uniform(-2, 2),
                action.end_y + random.uniform(-2, 2)
            )

            logger.info(f"Human mouse move: ({action.start_x},{action.start_y}) → ({action.end_x},{action.end_y})")

            return {
                "status": "success",
                "content": [{
                    "json": {
                        "action": "human_mouse_move",
                        "start": {"x": action.start_x, "y": action.start_y},
                        "end": {"x": action.end_x, "y": action.end_y}
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Human mouse move failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Human mouse move failed: {str(e)}"}]}

    async def _async_press_and_hold(self, action: PressAndHoldAction) -> Dict[str, Any]:
        """Press and hold mouse button"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            await page.mouse.down()
            await asyncio.sleep(action.hold_time)
            await page.mouse.up()

            logger.info(f"Press and hold for {action.hold_time}s")

            return {
                "status": "success",
                "content": [{
                    "json": {
                        "action": "press_and_hold",
                        "holdTime": action.hold_time
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Press and hold failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Press and hold failed: {str(e)}"}]}

    async def _async_screenshot(self, action: ScreenshotAction) -> Dict[str, Any]:
        """Take screenshot and return image data"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            screenshot_bytes = await page.screenshot(type='png', timeout=15000, animations='disabled')

            logger.info("Screenshot captured")

            return {
                "status": "success",
                "content": [{
                    "image": {
                        "format": 'png',
                        "source": {
                            "bytes": screenshot_bytes
                        }
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Screenshot failed: {str(e)}"}]}

    async def _async_get_text(self, action: GetTextAction) -> Dict[str, Any]:
        """Get element text"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            text = await page.text_content(action.selector, timeout=15000)

            return {"status": "success", "content": [{"text": text or ""}]}
        except Exception as e:
            logger.error(f"Get text failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Get text failed: {str(e)}"}]}

    async def _async_get_html(self, action: GetHtmlAction) -> Dict[str, Any]:
        """Get page HTML"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            html = await page.content()

            return {"status": "success", "content": [{"text": html}]}
        except Exception as e:
            logger.error(f"Get HTML failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Get HTML failed: {str(e)}"}]}

    async def _async_evaluate(self, action: EvaluateAction) -> Dict[str, Any]:
        """Execute JavaScript"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            result = await page.evaluate(action.script)

            return {"status": "success", "content": [{"json": result}]}
        except Exception as e:
            logger.error(f"Evaluate failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Evaluate failed: {str(e)}"}]}

    async def _async_wait(self, action: WaitAction) -> Dict[str, Any]:
        """Wait for specified time"""
        await asyncio.sleep(action.timeout)
        return {"status": "success", "content": [{"json": {"waited": action.timeout}}]}

    async def _async_new_tab(self, action: NewTabAction) -> Dict[str, Any]:
        """Open new tab"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            new_page = await session.context.new_page()
            tab_id = f"tab_{len(session.tabs)}"
            session.add_tab(tab_id, new_page)
            session.set_active_tab(tab_id)

            logger.info(f"Opened new tab: {tab_id}")

            return {"status": "success", "content": [{"json": {"tabId": tab_id}}]}
        except Exception as e:
            logger.error(f"New tab failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"New tab failed: {str(e)}"}]}

    async def _async_switch_tab(self, action: SwitchTabAction) -> Dict[str, Any]:
        """Switch to tab"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        if action.tab_id not in session.tabs:
            return {"status": "error", "content": [{"text": f"Tab '{action.tab_id}' not found"}]}

        session.set_active_tab(action.tab_id)
        logger.info(f"Switched to tab: {action.tab_id}")

        return {"status": "success", "content": [{"json": {"tabId": action.tab_id}}]}

    async def _async_list_tabs(self, action: ListTabsAction) -> Dict[str, Any]:
        """List all tabs including untracked context pages"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            page = session.get_active_page()
            context = page.context

            # Wait and check for new pages multiple times
            for wait_round in range(5):  # Check 5 times over 5 seconds
                await asyncio.sleep(1)

                all_pages = context.pages
                tracked_pages = set(session.tabs.values())

                # Add any untracked pages to session tabs
                for context_page in all_pages:
                    if context_page not in tracked_pages:
                        try:
                            new_title = await context_page.title()
                            new_tab_id = new_title
                        except Exception:
                            new_tab_id = f"tab_{len(session.tabs) + 1}"

                        session.add_tab(new_tab_id, context_page)
                        logger.info(f"Found untracked tab: '{new_tab_id}'")

            # Build tabs info
            tabs_info = {}
            for tab_id, page in session.tabs.items():
                try:
                    is_active = tab_id == session.active_tab_id
                    tabs_info[tab_id] = {"url": page.url, "active": is_active}
                except Exception as e:
                    tabs_info[tab_id] = {"error": f"Could not retrieve tab info: {str(e)}"}

            logger.info(f"Listed {len(session.tabs)} session tabs")

            import json
            return {"status": "success", "content": [{"text": json.dumps(tabs_info, indent=2)}]}

        except Exception as e:
            logger.error(f"Failed to list tabs: {str(e)}")
            return {"status": "error", "content": [{"text": f"Failed to list tabs: {str(e)}"}]}

    async def _async_close(self, action: CloseAction) -> Dict[str, Any]:
        """Close session"""
        session = self._sessions.get(action.session_name)
        if not session:
            return {"status": "error", "content": [{"text": f"Session '{action.session_name}' not found"}]}

        try:
            await session.browser.close()
            del self._sessions[action.session_name]
            logger.info(f"Closed session: {action.session_name}")

            return {"status": "success", "content": [{"json": {"sessionName": action.session_name}}]}
        except Exception as e:
            logger.error(f"Close failed: {str(e)}")
            return {"status": "error", "content": [{"text": f"Close failed: {str(e)}"}]}
