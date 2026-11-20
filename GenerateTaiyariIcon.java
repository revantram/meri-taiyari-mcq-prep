import java.awt.*;
import java.awt.geom.*;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

public class GenerateTaiyariIcon {

    public static BufferedImage createIcon(int size) {
        BufferedImage img = new BufferedImage(size, size, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        double s = size / 512.0;

        // Base rounded rect (iOS squircle style)
        double corner = 110 * s;
        RoundRectangle2D.Double squircle = new RoundRectangle2D.Double(0, 0, size, size, corner, corner);
        g.setClip(squircle);

        // Vibrant liquid background gradient
        GradientPaint bgPaint = new GradientPaint(
            0, 0, new Color(30, 58, 138), // deep royal blue
            size, size, new Color(37, 99, 235) // vibrant blue
        );
        g.setPaint(bgPaint);
        g.fill(squircle);

        // Subtle decorative glass gradient accent
        RadialGradientPaint glassGlow = new RadialGradientPaint(
            new Point2D.Double(size * 0.3, size * 0.25),
            (float)(size * 0.65),
            new float[]{0.0f, 0.6f, 1.0f},
            new Color[]{new Color(96, 165, 250, 140), new Color(59, 130, 246, 50), new Color(0, 0, 0, 0)}
        );
        g.setPaint(glassGlow);
        g.fill(squircle);

        // Center glowing circle target
        double cx = size / 2.0;
        double cy = size * 0.46;
        double cr = 140 * s;

        g.setPaint(new Color(255, 255, 255, 30));
        g.fill(new Ellipse2D.Double(cx - cr - 20 * s, cy - cr - 20 * s, (cr + 20 * s) * 2, (cr + 20 * s) * 2));

        g.setPaint(new Color(255, 255, 255, 45));
        g.fill(new Ellipse2D.Double(cx - cr, cy - cr, cr * 2, cr * 2));

        // Inner golden medal / badge
        GradientPaint badgeGrad = new GradientPaint(
            (float)(cx - cr * 0.75), (float)(cy - cr * 0.75), new Color(251, 191, 36),
            (float)(cx + cr * 0.75), (float)(cy + cr * 0.75), new Color(245, 158, 11)
        );
        g.setPaint(badgeGrad);
        g.fill(new Ellipse2D.Double(cx - cr * 0.75, cy - cr * 0.75, cr * 1.5, cr * 1.5));

        // White emblem: Target / Checkmark / Star in center
        g.setPaint(Color.WHITE);
        g.setStroke(new BasicStroke((float)(14 * s), BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        Path2D.Double check = new Path2D.Double();
        check.moveTo(cx - 45 * s, cy - 5 * s);
        check.lineTo(cx - 10 * s, cy + 30 * s);
        check.lineTo(cx + 48 * s, cy - 35 * s);
        g.draw(check);

        // Top glossy flare
        g.setClip(null);
        g.setPaint(new GradientPaint(
            0, 0, new Color(255, 255, 255, 90),
            0, (float)(size * 0.5), new Color(255, 255, 255, 0)
        ));
        g.fill(new RoundRectangle2D.Double(0, 0, size, size * 0.45, corner, corner));

        // Border outline
        g.setPaint(new Color(255, 255, 255, 60));
        g.setStroke(new BasicStroke((float)(3 * s)));
        g.draw(squircle);

        g.dispose();
        return img;
    }

    public static void main(String[] args) throws Exception {
        String baseDir = "/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app";
        int[] sizes = {512, 192, 144, 96, 72, 48};
        
        // PWA icons
        ImageIO.write(createIcon(512), "png", new File(baseDir + "/assets/icon-512.png"));
        ImageIO.write(createIcon(192), "png", new File(baseDir + "/assets/icon-192.png"));
        ImageIO.write(createIcon(192), "png", new File(baseDir + "/assets/ic_launcher.png"));

        // Android mipmaps
        ImageIO.write(createIcon(192), "png", new File(baseDir + "/android/res/mipmap-xxhdpi/ic_launcher.png"));
        ImageIO.write(createIcon(144), "png", new File(baseDir + "/android/res/mipmap-xhdpi/ic_launcher.png"));
        ImageIO.write(createIcon(96), "png", new File(baseDir + "/android/res/mipmap-hdpi/ic_launcher.png"));

        System.out.println("App icons generated successfully!");
    }
}
