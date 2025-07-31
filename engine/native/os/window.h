#include <stdexcept>
#include <string>

#include <SDL3/SDL.h>

namespace TorsionEngine::OS
{
	/// @brief Changes the way a window is displayed on the screen
	enum class WindowMode 
	{
		/// @brief Displays the window onto a rectangular area that can be moved around freely
		Windowed,
		/// @brief Displays the window over the entire screen and cannot be moved
		Fullscreen,
		/// @brief Windowed mode mimicing Fullscreen mode, can solve problems like alt+tab
		BorderlessWindowed
	};

	/// @brief Settings used for the creation of the window
	struct WindowSettings
	{
		std::string title = "Torsion Engine";
		std::string icon = "";
		int width = 1280;
		int height = 720;
		int x = SDL_WINDOWPOS_CENTERED;
		int y = SDL_WINDOWPOS_CENTERED;
		bool resizable = true;
		WindowMode mode;
	};

	/// @brief OS class for handling and processing native windows
	class Window
	{
	public:
		explicit Window(const WindowSettings& settings);
		~Window();

		/// @brief Polls and processes all window events
		void Update();

		/// @brief Changes the window's close request state
		/// @param close Whether this window wants to close
		void SetClose(const bool close) { _closeRequest = close; }

		/// @brief Changes the window's current name
		/// @param title The window's new name
		void SetTitle(const std::string& title);

		/// @brief Changes the window's current icon
		/// @param icon The path to the window's new icon
		void SetIcon(const std::string& icon);

		/// @brief Sets whether this window can be resized by the user
		/// @param resizable Can the user resize this window
		void SetResizable(const bool resizable);

		/// @brief Changes the window's current mode
		/// @note I.E. Fullscreen, Windowed, etc
		/// @param mode The window's new mode
		void SetMode(const WindowMode mode);

		/// @brief Changes the window's current size in pixels
		/// @param width The window's width in pixels
		/// @param height The window's height in pixels
		void Resize(const int width, const int height);

		/// @brief Changes the window's current position in pixels
		/// @param x The window's new x coordinate in pixels
		/// @param y The window's new y coordinate in pixels
		void Move(const int x, const int y);

		/// @brief Moves the window to the center of the screen
		void Center() { Move(SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED); }
		
		/// @brief Returns the window's current close request
		/// @return True if it wants to close, false if it doesn't
		[[nodiscard]] bool NeedsToClose() const { return _closeRequest; }

		/// @brief Returns the handle of the window
		/// @return The window handle
		[[nodiscard]] SDL_Window* GetHandle() const { return _window; }
	private:
		SDL_Window* _window;
		std::string _title;
		std::string _icon;
		int _width, _height;
		int _x, _y;
		WindowMode _mode;
		bool _closeRequest = false;
		bool _resizable = true;

		/// @brief Checks if the window can be moved or resized
		/// @return True if this window can be moved/resized, or False if not
		bool IsRectModifiable() { return _mode == WindowMode::Windowed; }
	};
}