package com.husarp.recklessdriving;

import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * In-app updating for the Android build.
 *
 * Batch 579, direct request ("like Lexling"): the new version is downloaded by Android's own download
 * service - the progress in the notification bar, even with the game closed, and the file in Downloads,
 * named with its version. The game never installs it: the player opens the file (the finished download's
 * notification, or the Downloads list openDownloads() shows) and the phone's own installer does it. So
 * the game needs no permission to install apps; if Android asks at all, it asks once about the Files /
 * Downloads app. It used to download the APK itself and hand it to the installer, which needed
 * "allow Reckless Driving to install unknown apps". Same plugin as Lexling's UpdateDownloadPlugin.
 */
@CapacitorPlugin(name = "AppUpdate")
public class AppUpdatePlugin extends Plugin {

    /**
     * Batch 537: open a URL in the phone's browser.
     *
     * The game's own GITHUB button needs this because window.open() does nothing in an Android
     * WebView unless the host opts into multiple windows - so without a native route the button
     * would look fine and simply never do anything, which is the exact problem it was added to fix.
     *
     * FLAG_ACTIVITY_NEW_TASK is required: the intent is started from an Activity context but has to
     * launch the browser as its own task, or Android refuses it outright.
     */
    @PluginMethod
    public void openUrl(PluginCall call) {
        final String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("No URL was given");
            return;
        }
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(intent);
            call.resolve();
        } catch (Exception e) {
            call.reject("Could not open the link: " + e.getMessage());
        }
    }

    private DownloadManager manager() {
        return (DownloadManager) getContext().getSystemService(Context.DOWNLOAD_SERVICE);
    }

    /** Starts downloading `url` as `name` into Downloads. Resolves with the download's id. */
    @PluginMethod
    public void download(PluginCall call) {
        String url = call.getString("url"), name = call.getString("name", "RecklessDriving.apk");
        DownloadManager m = manager();
        if (url == null || m == null) {
            call.reject("No download URL was given");
            return;
        }
        try {
            DownloadManager.Request r = new DownloadManager.Request(Uri.parse(url))
                    .setTitle(call.getString("title", name))
                    .setMimeType("application/vnd.android.package-archive")
                    .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            // Downloads, where the player finds it. Android 10 and later need no permission for that; older
            // ones keep it in the download service's own place, still openable from its notification.
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                r.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, name);
            }
            JSObject o = new JSObject();
            o.put("id", String.valueOf(m.enqueue(r)));
            call.resolve(o);
        } catch (RuntimeException e) {
            call.reject("Could not start the download: " + e.getMessage());
        }
    }

    /** How the download `id` is doing: status running / done / failed, and its bytes so far out of the whole. */
    @PluginMethod
    public void progress(PluginCall call) {
        DownloadManager m = manager();
        long id;
        try {
            id = Long.parseLong(call.getString("id", ""));
        } catch (NumberFormatException e) {
            call.reject("No such download");
            return;
        }
        JSObject o = new JSObject();
        try (Cursor c = m == null ? null : m.query(new DownloadManager.Query().setFilterById(id))) {
            if (c == null || !c.moveToFirst()) {
                o.put("status", "failed");
                call.resolve(o);
                return;
            }
            int status = c.getInt(c.getColumnIndexOrThrow(DownloadManager.COLUMN_STATUS));
            o.put("status", status == DownloadManager.STATUS_SUCCESSFUL ? "done"
                    : status == DownloadManager.STATUS_FAILED ? "failed" : "running");
            o.put("done", c.getLong(c.getColumnIndexOrThrow(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR)));
            o.put("total", c.getLong(c.getColumnIndexOrThrow(DownloadManager.COLUMN_TOTAL_SIZE_BYTES)));
            call.resolve(o);
        }
    }

    /** The download `id` and its file gone - the new version runs, so the file that brought it is not needed. */
    @PluginMethod
    public void remove(PluginCall call) {
        DownloadManager m = manager();
        try {
            if (m != null) m.remove(Long.parseLong(call.getString("id", "")));
        } catch (RuntimeException e) {
            // gone already
        }
        call.resolve();
    }

    /** The phone's list of downloads - where the player taps the file to install it. */
    @PluginMethod
    public void openDownloads(PluginCall call) {
        Intent list = new Intent(DownloadManager.ACTION_VIEW_DOWNLOADS);
        list.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        getContext().startActivity(list);
        call.resolve();
    }
}
