Console.WriteLine("Hello, World!");

try
{
    var settings = new WindowSettings
    {
        title = "Test Window",
        width = 800,
        height = 600,
        mode = WindowMode.Windowed
    };

    Window.Init();

    using var window = new Window(settings);

    while (!window.NeedsToClose())
    {
        try
        {
            window.Update();
            Thread.Sleep(16); // ~60 FPS - prevent tight loop
        }
        catch (AccessViolationException ex)
        {
            Console.WriteLine($"Error during update: {ex.Message}");
            break;
        }
    }
}
catch (Exception ex)
{
    Console.WriteLine($"Error creating window: {ex.Message}");
}
Window.Quit();

Console.WriteLine("Press any key to exit...");
Console.ReadKey();