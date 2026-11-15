"""Drive the compact step picker without depending on a guide's number of steps."""
import re


def choose_tree_step(view, label, *, keyboard=False):
    picker = view.locator('.lesson-tree-step-picker').filter(
        has=view.page.locator('button').filter(has_text=re.compile(f'^{re.escape(label)}$')))
    summary = picker.locator('summary')
    if keyboard:
        summary.press('Enter')
        picker.get_by_role('button', name=label, exact=True).press('Enter')
    else:
        summary.click()
        picker.get_by_role('button', name=label, exact=True).click()
