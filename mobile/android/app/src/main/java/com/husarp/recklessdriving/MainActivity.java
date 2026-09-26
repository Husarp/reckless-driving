package com.husarp.recklessdriving;

import android.os.Bundle;
import android.view.View;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        // Must run before super.onCreate: the bridge is built there, and a plugin registered
        // afterwards is invisible to the web layer.
        registerPlugin(AppUpdatePlugin.class);
        registerPlugin(SaveTransferPlugin.class);   // Batch 564 - TRANSFER SAVE
        super.onCreate(savedInstanceState);
        goImmersive();
    }

    /**
     * Batch 514, direct report: "the navigation bar and the controls at the top don't disappear in
     * the game" and "the game should take up all of your screen".
     *
     * The game's own FULLSCREEN setting called document.documentElement.requestFullscreen(), which
     * is a no-op in an Android WebView unless the host implements onShowCustomView - so the bars
     * never went anywhere however the setting was set. Hiding them is the host's job, so the host
     * does it.
     *
     * Sticky immersive rather than a hard hide: a swipe from an edge still brings the bars back for
     * a few seconds, so the phone never feels like it has trapped you, and they slide away again on
     * their own. setDecorFitsSystemWindows(false) is what lets the page extend under the cutout -
     * the CSS already handles that with env(safe-area-inset-*), so nothing ends up beneath the
     * camera island.
     */
    private void goImmersive() {
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        WindowInsetsControllerCompat controller =
                WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        controller.hide(WindowInsetsCompat.Type.systemBars());
        controller.setSystemBarsBehavior(
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        // The bars come back whenever the window loses and regains focus - after a notification
        // shade pull, a permission dialog, or the transient swipe above. Without this the game
        // quietly loses its full screen partway through a session and never gets it back.
        if (hasFocus) goImmersive();
    }

    /**
     * Batch 514, direct report: the Android back gesture did nothing at all.
     *
     * The web layer decides, because it is the only side that knows which screen is open. It
     * returns true when it handled the press; anything else - including an error, or a page that
     * has not finished loading and has no handler yet - falls through to Android's own behaviour,
     * so back can never become a dead button.
     */
    @Override
    public void onBackPressed() {
        if (bridge == null || bridge.getWebView() == null) {
            super.onBackPressed();
            return;
        }
        bridge.getWebView().evaluateJavascript(
                "(function(){try{return !!(window.__androidBack && window.__androidBack());}catch(e){return false;}})()",
                value -> {
                    if (!"true".equals(value)) {
                        runOnUiThread(() -> MainActivity.super.onBackPressed());
                    }
                });
    }
}
