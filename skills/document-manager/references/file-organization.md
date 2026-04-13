# File Organization Reference

## Analysis Commands

```bash
# Get overview of current structure
ls -la [target_directory]

# Check file types
find [target_directory] -type f -exec file {} \; | head -20

# Identify largest files
du -sh [target_directory]/* | sort -rh | head -20

# Count file types
find [target_directory] -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

## Duplicate Detection

```bash
# Find exact duplicates by hash
find [directory] -type f -exec md5 {} \; | sort | uniq -d

# Find files with same name
find [directory] -type f -printf '%f\n' | sort | uniq -d

# Find similar-sized files
find [directory] -type f -printf '%s %p\n' | sort -n
```

## Execution Commands

```bash
# Create folder structure
mkdir -p "path/to/new/folders"

# Move files with clear logging
mv "old/path/file.pdf" "new/path/file.pdf"

# Find files modified this week
find . -type f -mtime -7
```

## Organization Patterns

### By Type
- Documents (PDFs, DOCX, TXT)
- Images (JPG, PNG, SVG)
- Videos (MP4, MOV)
- Archives (ZIP, TAR, DMG)
- Code/Projects (directories with code)
- Spreadsheets (XLSX, CSV)
- Presentations (PPTX, KEY)

### By Purpose
- Work vs. Personal
- Active vs. Archive
- Project-specific
- Reference materials
- Temporary/scratch files

### By Date
- Current year/month
- Previous years
- Very old (archive candidates)

## Proposed Structure Template

```
[Directory]/
├── Work/
│   ├── Projects/
│   ├── Documents/
│   └── Archive/
├── Personal/
│   ├── Photos/
│   ├── Documents/
│   └── Media/
└── Downloads/
    ├── To-Sort/
    └── Archive/
```

## Photo Organization

Photos organized by EXIF or modification date:
```
Photos/
├── 2023/
│   ├── 01-January/
│   ├── 02-February/
│   └── ...
├── 2024/
│   └── ...
└── Unsorted/
```

## Folder Naming Conventions

- Use clear, descriptive names
- Avoid spaces (use hyphens or underscores)
- Be specific: "client-proposals" not "docs"
- Use prefixes for ordering: "01-current", "02-archive"

## File Naming Conventions

- Include dates: "2024-10-17-meeting-notes.md"
- Be descriptive: "q3-financial-report.xlsx"
- Avoid version numbers in names (use version control instead)
- Remove download artifacts: "document-final-v2 (1).pdf" → "document.pdf"
- Important files: "YYYY-MM-DD - Description.ext"

## When to Archive

- Projects not touched in 6+ months
- Completed work that might be referenced later
- Old versions after migration to new systems
- Files you're hesitant to delete (archive first, then delete later)

## Maintenance Schedule

- **Weekly**: Sort new downloads
- **Monthly**: Review and archive completed projects
- **Quarterly**: Check for new duplicates
- **Yearly**: Archive old files
