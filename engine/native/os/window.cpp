#include "window.h"

namespace TorsionEngine::OS
{
    Window::Window(const WindowSettings& settings)
        : _title(settings.title), _width(settings.width),
        _height(settings.height), _x(settings.x), 
        _y(settings.y), _resizable(settings.resizable)
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

        Move(_x, _y);
        SetResizable(_resizable);
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
        SDL_Event* e;
        while (SDL_PollEvent(e))
        {
            if (e->type == SDL_EVENT_QUIT)
            {
                SetClose(true);
            }
        }
    }

    void Window::SetTitle(const std::string& title)
    {
        SDL_SetWindowTitle(_window, title.c_str());
        _title = title;
    }

    void Window::SetResizable(const bool resizable)
    {
        if (_resizable == resizable) return;

        SDL_SetWindowResizable(_window, resizable);
        _resizable = resizable;
    }

    void Window::Resize(const int width, const int height)
    {
        if (width <= 0 || height <= 0) return;

        SDL_SetWindowSize(_window, width, height);
        _width = width;
        _height = height;
    }

    void Window::Move(const int x, const int y)
    {
        SDL_SetWindowPosition(_window, x, y);
        _x = x;
        _y = y;
    }
}