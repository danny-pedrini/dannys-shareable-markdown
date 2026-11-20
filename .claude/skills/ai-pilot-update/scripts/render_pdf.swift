// Render a Drive PDF export to one PNG per page, with each page's text and links.
//
// Usage: swift <skill>/scripts/render_pdf.swift <export.json|file.pdf> <out-dir> [scale]
//
// <export.json> is the saved result of Drive export_file ({name, mimeType, format, base64}).
// Writes <out-dir>/page-01.png ..., page-01.txt ... (full page text), pages.tsv (page number,
// first 100 characters) and links.tsv (page number, link URL).
// Exits non-zero when the input does not decode to a PDF or a page fails to render.
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write("usage: render_pdf.swift <export.json|file.pdf> <out-dir> [scale]\n".data(using: .utf8)!)
    exit(2)
}
let input = URL(fileURLWithPath: args[1])
let outDir = URL(fileURLWithPath: args[2])
let scale = args.count > 3 ? CGFloat(Double(args[3]) ?? 2.0) : 2.0

guard var data = try? Data(contentsOf: input) else {
    FileHandle.standardError.write("render_pdf: cannot read \(input.path)\n".data(using: .utf8)!)
    exit(1)
}
if input.pathExtension.lowercased() == "json" || input.pathExtension.lowercased() == "txt" {
    guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let b64 = obj["base64"] as? String,
          let decoded = Data(base64Encoded: b64) else {
        FileHandle.standardError.write("render_pdf: \(input.path) is not an export_file result with a base64 field\n".data(using: .utf8)!)
        exit(1)
    }
    data = decoded
}
guard let doc = PDFDocument(data: data) else {
    FileHandle.standardError.write("render_pdf: input does not decode to a PDF\n".data(using: .utf8)!)
    exit(1)
}
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)
var tsv = "page\tfirst_text\n"
var links = "page\turl\n"
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { exit(1) }
    let box = page.bounds(for: .mediaBox)
    let size = NSSize(width: box.width * scale, height: box.height * scale)
    let image = page.thumbnail(of: size, for: .mediaBox)
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:]) else {
        FileHandle.standardError.write("render_pdf: page \(i + 1) failed to render\n".data(using: .utf8)!)
        exit(1)
    }
    let name = String(format: "page-%02d.png", i + 1)
    try png.write(to: outDir.appendingPathComponent(name))
    let full = page.string ?? ""
    try full.write(to: outDir.appendingPathComponent(String(format: "page-%02d.txt", i + 1)), atomically: true, encoding: .utf8)
    let text = full.replacingOccurrences(of: "\n", with: " ").replacingOccurrences(of: "\t", with: " ")
    tsv += "\(i + 1)\t\(String(text.prefix(100)))\n"
    for a in page.annotations {
        if let u = a.url { links += "\(i + 1)\t\(u.absoluteString)\n" }
        else if let action = a.action as? PDFActionURL, let u = action.url { links += "\(i + 1)\t\(u.absoluteString)\n" }
    }
}
try tsv.write(to: outDir.appendingPathComponent("pages.tsv"), atomically: true, encoding: .utf8)
try links.write(to: outDir.appendingPathComponent("links.tsv"), atomically: true, encoding: .utf8)
print("rendered \(doc.pageCount) pages to \(outDir.path)")
