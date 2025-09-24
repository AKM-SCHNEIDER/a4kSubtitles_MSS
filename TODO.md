# TODO: Add Manual Search Feature to a4kSubtitles Addon

## Steps to Complete

1. **Modify core.py**:
   - Update the 'manualsearch' action to prompt for user input instead of showing notification.
   - Add logic to collect manual metadata (title, year, type, season/episode).
   - Route to search with manual metadata.

2. **Enhance kodi.py**:
   - Add helper functions for manual input dialogs using xbmcgui.Dialog.

3. **Update search.py**:
   - Modify search function to accept optional manual metadata parameters.
   - Skip automatic metadata extraction if manual data is provided.
   - Handle missing IMDB ID gracefully for manual searches.

4. **Update video.py**:
   - Add function to create metadata object from manual input.

5. **Integration and Testing**:
   - Ensure manual search integrates with Kodi UI.
   - Test the feature in Kodi environment.
   - Handle edge cases and errors.

6. **Add Exception Handling**:
   - Add comprehensive try-catch blocks to all critical functions in search.py
   - Prevent crashes from unhandled exceptions during search operations
   - Log errors appropriately for debugging

## Progress
- [x] Step 1: Modify core.py
- [x] Step 2: Enhance kodi.py
- [x] Step 3: Update search.py
- [x] Step 4: Update video.py
- [x] Step 5: Integration and Testing
- [x] Step 6: Add Exception Handling
