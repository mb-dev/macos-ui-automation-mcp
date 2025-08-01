// Example Screenshot Implementation for macOS Apps
// Based on implementation from task-management project
// Add this to your Mac app to enable screenshot functionality that can be triggered via Playwright MCP

import Foundation
import ScreenCaptureKit
import AppKit

/// Manager for taking screenshots of the application
@available(macOS 14.0, *)
public class ScreenshotManager: ObservableObject {
    public static let shared = ScreenshotManager()
    
    private init() {}
    
    /// Take a screenshot of the current app window and save it to the specified directory
    @MainActor
    public func takeAppScreenshot(saveToDirectory: String? = nil) async throws -> URL {
        print("Taking screenshot of application window")
        
        // Get shareable content
        let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
        
        // Find our app window
        guard let appWindow = findAppWindow(in: content.windows) else {
            throw ScreenshotError.appWindowNotFound
        }
        
        print("Found app window: \(appWindow.title ?? "Untitled") (ID: \(appWindow.windowID))")
        
        // Configure capture settings for high quality
        let configuration = SCStreamConfiguration()
        configuration.captureResolution = .best
        configuration.pixelFormat = kCVPixelFormatType_32BGRA
        configuration.scalesToFit = false
        configuration.preservesAspectRatio = true
        configuration.capturesAudio = false
        
        // Set dimensions based on window size
        let windowFrame = appWindow.frame
        configuration.width = Int(windowFrame.width * 2) // 2x for retina
        configuration.height = Int(windowFrame.height * 2)
        
        // Create filter for just our window
        let filter = SCContentFilter(desktopIndependentWindow: appWindow)
        
        print("Capturing window with dimensions: \(configuration.width)x\(configuration.height)")
        
        // Capture the image
        let capturedImage = try await SCScreenshotManager.captureImage(contentFilter: filter, configuration: configuration)
        
        // Generate filename with timestamp
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd_HH-mm-ss"
        let timestamp = formatter.string(from: Date())
        let filename = "\(Bundle.main.infoDictionary?["CFBundleName"] as? String ?? "App")_\(timestamp).png"
        
        // Determine save directory
        let saveDirectory = saveToDirectory ?? {
            let documentsPath = FileManager.default.urls(for: .documentsDirectory, in: .userDomainMask).first!
            return documentsPath.appendingPathComponent("Screenshots").path
        }()
        
        // Create screenshots directory if it doesn't exist
        try FileManager.default.createDirectory(atPath: saveDirectory, withIntermediateDirectories: true)
        
        // Create absolute path
        let absolutePath = URL(fileURLWithPath: saveDirectory).appendingPathComponent(filename)
        
        // Save to file
        let nsImage = NSImage(cgImage: capturedImage, size: NSZeroSize)
        guard let tiffData = nsImage.tiffRepresentation,
              let bitmapRep = NSBitmapImageRep(data: tiffData),
              let pngData = bitmapRep.representation(using: .png, properties: [:]) else {
            throw ScreenshotError.failedToConvertImage
        }
        
        try pngData.write(to: absolutePath)
        
        print("Screenshot saved to: \(absolutePath.path)")
        return absolutePath
    }
    
    /// Find the app window (customize this for your app)
    private func findAppWindow(in windows: [SCWindow]) -> SCWindow? {
        // Look for windows with our app's bundle identifier
        let candidates = windows.filter { window in
            if let owningApp = window.owningApplication,
               owningApp.bundleIdentifier == Bundle.main.bundleIdentifier {
                return true
            }
            return false
        }
        
        // Return the largest window (likely the main window)
        return candidates.max { a, b in
            let aArea = a.frame.width * a.frame.height
            let bArea = b.frame.width * b.frame.height
            return aArea < bArea
        }
    }
}

/// Errors that can occur during screenshot operations
public enum ScreenshotError: Error, LocalizedError {
    case appWindowNotFound
    case failedToConvertImage
    case permissionDenied
    
    public var errorDescription: String? {
        switch self {
        case .appWindowNotFound:
            return "Could not find the app window"
        case .failedToConvertImage:
            return "Failed to convert captured image to PNG format"
        case .permissionDenied:
            return "Screen recording permission is required to take screenshots"
        }
    }
}

// MARK: - SwiftUI Integration Example

import SwiftUI

struct ContentView: View {
    @State private var showingScreenshotAlert = false
    @State private var screenshotPath: String = ""
    
    var body: some View {
        VStack {
            Text("My App")
                .font(.largeTitle)
            
            Button("Take Screenshot") {
                takeScreenshot()
            }
            .accessibilityIdentifier("screenshotButton") // Important: accessibility ID for MCP
            .help("Take a screenshot of this window")
        }
        .frame(minWidth: 400, minHeight: 300)
        .alert("Screenshot Saved", isPresented: $showingScreenshotAlert) {
            Button("OK") { }
        } message: {
            Text("Screenshot saved to: \(screenshotPath)")
        }
    }
    
    private func takeScreenshot() {
        Task {
            do {
                if #available(macOS 14.0, *) {
                    let screenshotManager = ScreenshotManager.shared
                    let screenshotURL = try await screenshotManager.takeAppScreenshot()
                    
                    await MainActor.run {
                        screenshotPath = screenshotURL.path
                        showingScreenshotAlert = true
                    }
                } else {
                    await MainActor.run {
                        screenshotPath = "Screenshot feature requires macOS 14.0+"
                        showingScreenshotAlert = true
                    }
                }
            } catch {
                print("Failed to take screenshot: \(error)")
                await MainActor.run {
                    screenshotPath = "Failed to take screenshot: \(error.localizedDescription)"
                    showingScreenshotAlert = true
                }
            }
        }
    }
}

// MARK: - Usage with Playwright MCP

/*
After implementing this in your app, you can use Playwright MCP to trigger screenshots:

Example commands to Claude:
- "Take a screenshot of the app by clicking the screenshot button"
- "Find the screenshot button and click it"
- "Click the button with accessibility identifier 'screenshotButton'"

The MCP will:
1. Find the button using: $..[?(@.ax_identifier=='screenshotButton')]
2. Click it using the click_by_accessibility_id tool
3. Your app will capture a screenshot and save it to ~/Documents/Screenshots/

Required permissions:
- Screen Recording permission in System Settings > Privacy & Security > Screen Recording
- Add your parent app (Terminal, VS Code, Claude Code) to the list

Required dependencies in Package.swift:
No additional dependencies needed - uses built-in ScreenCaptureKit (macOS 14.0+)
*/