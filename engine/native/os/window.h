#include <stdexcept>
#include <string>

#include <SDL3/SDL.h>

namespace TorsionEngine::OS
{
	/// @brief Settings used for the creation of the window
	struct WindowSettings
	{
		std::string title = "Torsion Engine";
		int width = 1280;
		int height = 720;
		int x = SDL_WINDOWPOS_CENTERED;
		int y = SDL_WINDOWPOS_CENTERED;
		bool resizable = true;
	};

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

		/// @brief Sets whether this window can be resized by the user
		/// @param resizable Can the user resize this window
		void SetResizable(const bool resizable);

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
		/// @return The window's close request state, true if it wants to close, false if it doesn't
		[[nodiscard]] bool NeedsToClose() const { return _closeRequest; }

		/// @brief Returns the handle of the window
		/// @return The window handle
		[[nodiscard]] SDL_Window* GetHandle() const { return _window; }
	private:
		SDL_Window* _window;
		std::string _title;
		int _width, _height;
		int _x, _y;
		bool _closeRequest = false;
		bool _resizable = true;
	};
}