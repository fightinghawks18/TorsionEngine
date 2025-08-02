#include "window.h"

namespace TorsionEngine::OS
{
    void Window::Init()
    {
        SDL_InitFlags initFlags = SDL_INIT_VIDEO;
        if (!SDL_WasInit(initFlags))
        {
            if (!SDL_Init(initFlags))
            {
                throw std::runtime_error("Failed to initialize SDL.");
            }
        }
    }

    void Window::Quit()
    {
        SDL_Quit();
    }

    Window::Window(const WindowSettings& settings)
        : _title(settings.title), _width(settings.width),
        _height(settings.height), _x(settings.x), 
        _y(settings.y), _resizable(settings.resizable),
        _mode(settings.mode), _icon(settings.icon)
    {
        SDL_WindowFlags flags = SDL_WINDOW_VULKAN;

        _window = SDL_CreateWindow(
            _title.c_str(),
            _width,
            _height,
            flags
        );

        if (_window == nullptr)
        {
            std::string error = "An error occurred when attempting to create a window:";
            error += SDL_GetError();
            throw std::runtime_error(error);
        }

        // Set properties after creation that aren't available in SDL_CreateWindow
        SetResizable(_resizable);
        SetMode(_mode);
        SetIcon(_icon);
        Move(_x, _y);
    }

    Window::~Window()
    {
        if (_window != nullptr)
        {
            SDL_DestroyWindow(_window);
            _window = nullptr;
        }
    }

    void Window::Update()
    {
        SDL_Event e;
        while (SDL_PollEvent(&e))
        {
            if (e.type == SDL_EVENT_QUIT)
            {
                SetClose(true);
            }
        }
    }

    void Window::SetTitle(const std::string& title)
    {
        if (_title == title) return;
        
        SDL_SetWindowTitle(_window, title.c_str());
        _title = title;
    }

    void Window::SetIcon(const std::string& icon)
    {
        if (icon.empty())
        {
            // Remove window icon
            SDL_SetWindowIcon(_window, nullptr);
        }
        else
        {
            // Create a readable texture for SDL
            SDL_Surface* iconSurface = SDL_LoadBMP(icon.c_str());
            if (iconSurface == nullptr)
            {
                std::string error = "Failed to create icon surface for window: ";
                error += SDL_GetError();
                throw std::runtime_error(error);
            }

            // Set and destroy window icon
            SDL_SetWindowIcon(_window, iconSurface);
            SDL_DestroySurface(iconSurface);
        }
        _icon = icon;
    }

    void Window::SetResizable(const bool resizable)
    {
        if (_resizable == resizable) return;

        SDL_SetWindowResizable(_window, resizable);
        _resizable = resizable;
    }

    void Window::SetMode(const WindowMode mode)
    {
        if (_mode == mode) return;

        switch (mode)
        {
            case WindowMode::Windowed:
            {
                SDL_SetWindowFullscreen(_window, false);

                // SDL_RestoreWindow exists but my functions allow changing rect in fullscreen
                Move(_x, _y);
                Resize(_width, _height);
                break;
            }
            case WindowMode::Fullscreen:
            {
                SDL_SetWindowFullscreen(_window, true);
                break;
            }
            case WindowMode::BorderlessWindowed:
            {
                SDL_SetWindowFullscreen(_window, false);
                SDL_SetWindowBordered(_window, false);
                SDL_MaximizeWindow(_window);
                break;
            }
        }

        _mode = mode;
    }

    void Window::Resize(const int width, const int height)
    {
        if (width <= 0 || height <= 0) return;

        _width = width;
        _height = height;

        if (!IsRectModifiable()) return;
        SDL_SetWindowSize(_window, width, height);
    }

    void Window::Move(const int x, const int y)
    {
        _x = x;
        _y = y;
        
        if (!IsRectModifiable()) return;
        SDL_SetWindowPosition(_window, x, y);
    }
}