from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async

from random import randint
import asyncio

from include.historiclal_data.race_results.dropdown_class import Dropdown


async def get_gp_race_results() -> dict:
    # close browser when we're finished with playwright
    async with async_playwright() as playwright:
        # launch chromium
        browser = await playwright.chromium.launch(headless=False, slow_mo=50)
        # create a new browser context
        context = await browser.new_context(
            color_scheme="dark",  # dark theme for Chromium
            locale="en-US,en;q=0.9",  # specifying the target language encoding
        )

        # open a new page
        page = await context.new_page()
        # apply stealth to the page
        await stealth_async(page)

        # direct the page to go to the specified URL
        await page.goto(
            "https://www.motogp.com/en/gp-results/2023/rsm/motogp/rac/classification",
            referer="https://www.google.com/",
        )

        # extract html from each session
        htmls = await extract_session_html(page)
        print(htmls.keys())


async def extract_session_html(page: Page) -> dict[str, str]:
    # initialize dict to store html from each session
    htmls = {}

    # get all years from "Year" dropdown
    years = await Dropdown.get_options(page, "year")
    # loop through years
    for year in years:
        # select year
        page = await Dropdown.select(page, Dropdown.css_selectors["year"], year)

        # get all events options
        events = await Dropdown.get_options(page, "event")
        # loop through events
        for event in events:
            # select event
            page = await Dropdown.select(page, Dropdown.css_selectors["event"], event)

            # get all category options
            categories = await Dropdown.get_options(page, "category")
            # loop through categories
            for cat in categories:
                # define selector
                selector = Dropdown.css_selectors["category"]
                # wait for option
                await Dropdown.wait_for_opts(page, selector, cat)
                # select category
                page = await Dropdown.select(page, selector, cat)

                # get all session options
                sessions = await Dropdown.get_options(page, "session")
                # define selector
                selector = Dropdown.css_selectors["category"]
                # wait for option
                await Dropdown.wait_for_opts(page, selector, "RAC")
                # continue with loop if RAC not in sessions
                if "RAC" not in sessions:
                    continue
                else:
                    page = await Dropdown.select(
                        page, Dropdown.css_selectors["session"], "RAC"
                    )

                    # append html to htmls
                    htmls.update({f"{year}_{event}_{cat}_RAC": await page.content()})

                # sleep for 1-5 seconds - to simulate non-robotic behavior
                await asyncio.sleep(randint(1, 7))

    # return htmls of each session
    return htmls


asyncio.run(get_gp_race_results())
