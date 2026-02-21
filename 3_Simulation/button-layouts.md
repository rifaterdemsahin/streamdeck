# Stream Deck Button Layouts and UI Examples

## Stream Deck XL #1 - DevOps/MLOps Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Row 1: Docker Operations                                        │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Docker   │ Docker   │ Restart  │ Clean    │ Compose  │ Logs     │
│ Status   │ PS       │ All      │ Images   │ Up       │ View     │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Row 2: Git Operations                                           │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Git      │ Quick    │ Push     │ Pull     │ Branch   │ Stash    │
│ Status   │ Commit   │ Origin   │ Latest   │ Switch   │ Changes  │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Row 3: Kubernetes/Cloud                                         │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ K8s      │ Get      │ Restart  │ Scale    │ Cloud    │ Monitor  │
│ Status   │ Pods     │ Deploy   │ Service  │ Deploy   │ Metrics  │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Row 4: MLOps Workflows                                          │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Train    │ Validate │ Deploy   │ Model    │ Data     │ Pipeline │
│ Model    │ Model    │ Staging  │ Metrics  │ Check    │ Run      │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

## Stream Deck XL #2 - Video Editing Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Row 1: DaVinci Resolve Project                                  │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ New      │ Import   │ Save     │ Export   │ Backup   │ Settings │
│ Project  │ Media    │ Project  │ Preset1  │ Project  │ Toggle   │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Row 2: Timeline Operations                                      │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Cut      │ Trim     │ Add      │ Delete   │ Ripple   │ Marker   │
│ Clip     │ Mode     │ Track    │ Track    │ Delete   │ Add      │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Row 3: Slideshow FX Plugin                                      │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Load     │ Template │ Apply    │ Adjust   │ Preview  │ Render   │
│ Plugin   │ 1        │ Effect   │ Timing   │ Effect   │ Slideshow│
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Row 4: Color & Effects                                          │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Color    │ Preset   │ Apply    │ Audio    │ Noise    │ Sharpen  │
│ Page     │ LUT      │ Grade    │ Sync     │ Reduce   │ Effect   │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

## Stream Deck + - AI & Utilities Layout

```
┌─────────────────────────────────────────┐
│ Row 1: AI Model Selection               │
├──────────┬──────────┬──────────┬────────┤
│ OpenAI   │ XAI      │ Claude   │ Local  │
│ GPT-4    │ Grok     │ Router   │ Model  │
└──────────┴──────────┴──────────┴────────┘

┌─────────────────────────────────────────┐
│ Row 2: Quick AI Actions                 │
├──────────┬──────────┬──────────┬────────┤
│ Code     │ Explain  │ Debug    │ Refact │
│ Review   │ Code     │ Error    │ -or    │
└──────────┴──────────┴──────────┴────────┘

┌─────────────────────────────────────────┐
│ Rotary Dial Functions:                  │
│ - Volume Control                         │
│ - AI Temperature Adjustment              │
│ - Brightness Control                     │
│ - Scroll Speed                           │
└─────────────────────────────────────────┘
```

## Stream Deck Mobile - Remote Monitoring

```
┌─────────────────────────────┐
│ Critical Status Display      │
├──────────┬─────────┬────────┤
│ System   │ Docker  │ K8s    │
│ Health   │ Status  │ Status │
├──────────┼─────────┼────────┤
│ CPU      │ Memory  │ Disk   │
│ Usage    │ Usage   │ Space  │
├──────────┼─────────┼────────┤
│ Emergency│ Stop    │ Restart│
│ Alert    │ All     │ System │
└──────────┴─────────┴────────┘
```

## Visual Indicators

### Color Coding
- **Green**: Success / Running / OK
- **Yellow**: Warning / Processing / Attention Needed
- **Red**: Error / Failed / Critical
- **Blue**: Info / Idle / Ready
- **Purple**: In Progress / Deploying

### Icon Design Guidelines
- Use simple, recognizable icons
- High contrast for visibility
- Consistent icon family
- Animated icons for active states
- Text labels for clarity

## Button Press Feedback
- Visual flash on press
- Status update after action
- Progress bar for long operations
- Toast notifications for results
- Audio feedback (optional)
