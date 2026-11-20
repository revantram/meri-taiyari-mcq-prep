package com.meritaiyari.app;

import android.app.Activity;
import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.print.PrintAttributes;
import android.print.PrintDocumentAdapter;
import android.print.PrintManager;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {

    private WebView mWebView;
    private long mLastBackPress = 0;

    public class WebAppInterface {
        private Context mContext;

        WebAppInterface(Context context) {
            mContext = context;
        }

        @JavascriptInterface
        public void showToast(String message) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public void printDocument(String jobName) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                        PrintManager printManager = (PrintManager) getSystemService(Context.PRINT_SERVICE);
                        PrintDocumentAdapter printAdapter = mWebView.createPrintDocumentAdapter();
                        if (printManager != null && printAdapter != null) {
                            printManager.print(jobName != null ? jobName : "मेरी तैयारी परीक्षा नोट्स", printAdapter, new PrintAttributes.Builder().build());
                        }
                    }
                }
            });
        }

        @JavascriptInterface
        public void fetchGoogleDocNative(final String urlString, final String callbackId) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        String finalUrl = urlString;
                        if (finalUrl.contains("/document/d/") && !finalUrl.contains("/export?format=txt")) {
                            int start = finalUrl.indexOf("/document/d/") + 12;
                            int end = finalUrl.indexOf("/", start);
                            String docId = (end != -1) ? finalUrl.substring(start, end) : finalUrl.substring(start);
                            if (docId.contains("?")) docId = docId.substring(0, docId.indexOf("?"));
                            finalUrl = "https://docs.google.com/document/d/" + docId + "/export?format=txt";
                        }

                        HttpURLConnection conn = (HttpURLConnection) new URL(finalUrl).openConnection();
                        conn.setInstanceFollowRedirects(true);
                        conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)");
                        conn.setConnectTimeout(15000);
                        conn.setReadTimeout(45000);

                        int status = conn.getResponseCode();
                        if (status == HttpURLConnection.HTTP_MOVED_TEMP || status == HttpURLConnection.HTTP_MOVED_PERM || status == 307) {
                            String redirectUrl = conn.getHeaderField("Location");
                            if (redirectUrl != null) {
                                conn.disconnect();
                                conn = (HttpURLConnection) new URL(redirectUrl).openConnection();
                                conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)");
                                conn.setConnectTimeout(15000);
                                conn.setReadTimeout(45000);
                            }
                        }

                        InputStream in = conn.getInputStream();
                        ByteArrayOutputStream out = new ByteArrayOutputStream();
                        byte[] buffer = new byte[8192];
                        int n;
                        while ((n = in.read(buffer)) > 0) {
                            out.write(buffer, 0, n);
                        }
                        in.close();
                        conn.disconnect();

                        final String content = new String(out.toByteArray(), StandardCharsets.UTF_8);
                        final String base64Content = Base64.encodeToString(content.getBytes(StandardCharsets.UTF_8), Base64.NO_WRAP);

                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                mWebView.evaluateJavascript("window.onNativeDocFetched('" + callbackId + "', true, '" + base64Content + "')", null);
                            }
                        });
                    } catch (final Exception e) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                mWebView.evaluateJavascript("window.onNativeDocFetched('" + callbackId + "', false, '" + e.getMessage().replace("'", "\\'") + "')", null);
                            }
                        });
                    }
                }
            }).start();
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        mWebView = new WebView(this);
        setContentView(mWebView);

        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);

        mWebView.setWebChromeClient(new WebChromeClient());
        mWebView.setWebViewClient(new WebViewClient());
        mWebView.addJavascriptInterface(new WebAppInterface(this), "AndroidNative");
        mWebView.addJavascriptInterface(new WebAppInterface(this), "AndroidInterface");

        mWebView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onBackPressed() {
        if (mWebView != null) {
            mWebView.evaluateJavascript("window.handleNativeBackPressed ? window.handleNativeBackPressed() : false", new ValueCallback<String>() {
                @Override
                public void onReceiveValue(String value) {
                    // If JavaScript handled the back navigation (closed workspace, modal, or detail screen)
                    if ("true".equalsIgnoreCase(value) || "\"true\"".equalsIgnoreCase(value)) {
                        return;
                    }

                    // Otherwise at root screen: double press back to exit
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            long now = System.currentTimeMillis();
                            if (now - mLastBackPress < 2000) {
                                finish();
                            } else {
                                mLastBackPress = now;
                                Toast.makeText(MainActivity.this, "बाहर निकलने के लिए एक बार फिर 'वापस' दबाएं", Toast.LENGTH_SHORT).show();
                            }
                        }
                    });
                }
            });
        } else {
            super.onBackPressed();
        }
    }
}
