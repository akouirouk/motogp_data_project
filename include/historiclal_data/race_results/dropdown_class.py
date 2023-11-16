from playwright.async_api import Page, TimeoutError

from typing import Literal

from include.helpers import text_to_num


class Dropdown:
    # css selectors for each dropdown in results page
    css_selectors = {
        "year": "select[class*='filter-select--year']",
        "event": "select[class*='filter-select--event']",
        "category": "div.primary-filter__filter-label:has-text('Category') + select.primary-filter__filter-select.primary-filter__filter-select--cat",
        "session": "div.primary-filter__filter-label:has-text('Session') + select.primary-filter__filter-select.primary-filter__filter-select--cat",
    }

    @classmethod
    async def wait_for_opts(cls, page: Page, selector: str, option: str) -> None:
        # wait for dropdown options
        await page.wait_for_selector(selector, timeout=10000)
        # wait for all options to be loaded - FIND OUT HOW TO DO THIS

    @classmethod
    async def get_options(
        cls, page: Page, dropdown_type: Literal["year", "event", "category", "session"]
    ) -> list[str]:
        # wait for page to be loaded
        await page.wait_for_load_state("domcontentloaded")

        # define selector
        selector = Dropdown.css_selectors[dropdown_type]
        # locate the dropdown
        dropdown = page.locator(selector)

        # click the dropdown to open options
        await dropdown.click()

        # list all options from the dropdown
        options = await dropdown.locator("option").all()
        # get the text of all options
        text_options = [await option.inner_text() for option in options]

        # if _type is year
        if dropdown_type == "year":
            # Use a list comprehension to apply the function to each element
            years_int = [text_to_num(year) for year in text_options]
            # get all years over 2012 (the start of the 1000cc era)
            text_options = [str(year) for year in years_int if 2023 <= year <= 2023]

        # strip whitespace from all elements in list
        text_options = [elem.strip() for elem in text_options]

        # return list of options for dropdown
        return text_options

    @classmethod
    async def is_matching(cls, page: Page, dropdown_elem: str, select_val: str) -> bool:
        """Check the current dropdown selection to see if it matches the selection

        Args:
            page (Page): The webpage object
            dropdown_elem (Page.locator): The HTML element for the dropdown element
            select_val (str): The option to select from the dropdown

        Returns:
            bool: Whether or not the selection matches the current selection
        """
        # how long to wait (in milliseconds) for selector to be visible
        wait_time = 10000

        try:
            # check for element visibility
            await page.wait_for_selector(dropdown_elem, timeout=wait_time)
        except:
            raise TimeoutError(
                f"Exceeded {wait_time / 1000} seconds waiting for {dropdown_elem} to be visible in page"
            )

        # locate the element
        locator = page.locator(dropdown_elem)
        # get the current selected value from the dropdown
        current_select = await locator.evaluate(
            f"(element) => element.options[element.selectedIndex].text"
        )

        # if the selection is equal to the current_select
        if select_val == current_select:
            return True
        # return by default
        return False

    @classmethod
    async def select(cls, page: Page, css_selector: str, selection: str) -> Page:
        """Select an option from the dropdown list

        Args:
            page (Page): The webpage object
            css_selector (str): The selector to the dropdown element
            selection (str): The option to select from the dropdown

        Raises:
            TimeoutError: If the selection is not an option in the dropdown element

        Returns:
            Page: The webpage object with changes to dropdown selection
        """
        # wait for page to be loaded
        await page.wait_for_load_state("domcontentloaded")

        # if the current selection is NOT the wanted selection
        if not await cls.is_matching(page, css_selector, selection):
            try:
                # wait for option
                await cls.wait_for_opts(page, css_selector, selection)
                # select option from dropdown
                await page.select_option(css_selector, label=selection)
            except TimeoutError as err:
                print(
                    TimeoutError(
                        f"Failed to select '{selection}' from element '{css_selector}'"
                    )
                )
                pass
        # wait for page load state
        await page.wait_for_load_state("domcontentloaded")
        # sleep for 1-5 seconds - to simulate non-robotic behavior
        # await asyncio.sleep(randint(1, 5))

        # return the page
        return page
