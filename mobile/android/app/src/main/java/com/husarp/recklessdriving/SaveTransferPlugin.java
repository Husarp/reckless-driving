package com.husarp.recklessdriving;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
import android.provider.Settings;

import androidx.activity.result.ActivityResult;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Batch 564: TRANSFER SAVE on Android - the two things the web page cannot do by itself.
 *
 * deviceId: ANDROID_ID. Since Android 8 it is fixed per signing key, user and phone, so it survives
 * reinstalling the game - which is exactly what a save sealed to one device needs. It changes only
 * on a factory reset. The game hashes it before showing it.
 *
 * saveFile: Android's own "save as" screen (ACTION_CREATE_DOCUMENT), so the player picks where the
 * file goes - Downloads, a USB stick, Google Drive - and no storage permission is needed. Exporting
 * wipes this device, so the file is read back after writing and returned as it actually is; the page
 * compares it byte for byte before it removes anything. Importing needs nothing here: the page's own
 * file picker already works in the WebView.
 */
@CapacitorPlugin(name = "SaveTransfer")
public class SaveTransferPlugin extends Plugin {

    @PluginMethod
    public void deviceId(PluginCall call) {
        String id = Settings.Secure.getString(getContext().getContentResolver(), Settings.Secure.ANDROID_ID);
        if (id == null || id.isEmpty()) {
            call.reject("This phone did not give an ID");
            return;
        }
        JSObject result = new JSObject();
        result.put("id", "android:" + id);
        call.resolve(result);
    }

    @PluginMethod
    public void saveFile(PluginCall call) {
        if (call.getString("text") == null) {
            call.reject("Nothing to save");
            return;
        }
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/octet-stream");
        intent.putExtra(Intent.EXTRA_TITLE, call.getString("name", "RecklessDriving.rdsave"));
        startActivityForResult(call, intent, "onSaveFilePicked");
    }

    @ActivityCallback
    private void onSaveFilePicked(PluginCall call, ActivityResult result) {
        if (call == null) return;
        Intent data = result.getData();
        if (result.getResultCode() != Activity.RESULT_OK || data == null || data.getData() == null) {
            JSObject cancelled = new JSObject();
            cancelled.put("status", "cancelled");
            call.resolve(cancelled);
            getBridge().releaseCall(call);   // saved by startActivityForResult; nothing frees it otherwise
            return;
        }
        final Uri uri = data.getData();
        final String text = call.getString("text");
        // Off the main thread: a cloud location can take a moment to write.
        new Thread(() -> {
            JSObject out = new JSObject();
            try {
                try (OutputStream stream = getContext().getContentResolver().openOutputStream(uri, "w")) {
                    if (stream == null) throw new Exception("could not open the file for writing");
                    stream.write(text.getBytes(StandardCharsets.UTF_8));
                }
                ByteArrayOutputStream back = new ByteArrayOutputStream();
                try (InputStream stream = getContext().getContentResolver().openInputStream(uri)) {
                    if (stream == null) throw new Exception("could not read the file back");
                    byte[] buffer = new byte[8192];
                    int read;
                    while ((read = stream.read(buffer)) > 0) back.write(buffer, 0, read);
                }
                out.put("status", "ok");
                out.put("name", displayName(uri));
                out.put("readBack", new String(back.toByteArray(), StandardCharsets.UTF_8));
            } catch (Exception e) {
                out.put("status", "failed");
                out.put("error", e.getMessage() != null ? e.getMessage() : e.toString());
            }
            call.resolve(out);
            getBridge().releaseCall(call);
        }).start();
    }

    /** The name the player will look for - the picker may have changed it (e.g. added "(1)"). */
    private String displayName(Uri uri) {
        try (Cursor c = getContext().getContentResolver().query(
                uri, new String[] { OpenableColumns.DISPLAY_NAME }, null, null, null)) {
            if (c != null && c.moveToFirst()) return c.getString(0);
        } catch (Exception ignored) {
            // fall through to the URI's own name
        }
        return uri.getLastPathSegment();
    }
}
