from atomacos import errors, converter, support, a11y
import pytest


class TestErrors:
    def test_error_message_in_exception(self):
        try:
            raise errors.AXErrorAPIDisabled("apple")
        except errors.AXError as e:
            assert "apple" in str(e)

    def test_set_known_code(self):
        with pytest.raises(errors.AXErrorAPIDisabled):
            errors.set_error(-25211, "test")
        with pytest.raises(errors.AXErrorInvalidUIElement):
            errors.set_error(-25202, "test")
        with pytest.raises(errors.AXErrorCannotComplete):
            errors.set_error(-25204, "test")
        with pytest.raises(errors.AXErrorNotImplemented):
            errors.set_error(-25208, "test")


class TestValueConversions:
    def test_convert_string(self):
        from CoreFoundation import (
            CFStringCreateWithCString,
            kCFStringEncodingASCII,
        )

        sut = CFStringCreateWithCString(None, b"hello", kCFStringEncodingASCII)
        result = converter.convert_value(sut)
        assert isinstance(result, str)
        assert result == "hello"

        sut = CFStringCreateWithCString(None, b"world", kCFStringEncodingASCII)
        result = converter.convert_value(sut)
        assert isinstance(result, str)
        assert result == "world"

    def test_convert_bool(self):
        from CoreFoundation import kCFBooleanTrue, kCFBooleanFalse

        result1 = converter.convert_value(kCFBooleanTrue)
        result2 = converter.convert_value(kCFBooleanFalse)

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        assert result1 is True
        assert result2 is False

    def test_convert_array(self):
        from CoreFoundation import CFArrayCreate, kCFTypeArrayCallBacks

        array = CFArrayCreate(None, [1, 2, 3, 4], 4, kCFTypeArrayCallBacks)
        result = converter.convert_value(array)
        assert isinstance(result, list)
        assert result == [1, 2, 3, 4]

    def test_convert_num_int(self):
        from CoreFoundation import CFNumberCreate, kCFNumberIntType

        num = CFNumberCreate(None, kCFNumberIntType, 1.5)
        result = converter.convert_value(num)
        assert result == 1
        assert isinstance(result, int)

    def test_convert_num_double(self):
        from CoreFoundation import CFNumberCreate, kCFNumberDoubleType

        num = CFNumberCreate(None, kCFNumberDoubleType, 1.5)
        result = converter.convert_value(num)
        assert result == 1.5
        assert isinstance(result, float)


class TestHelpers:
    def test_get_frontmost_pid(self):
        pid = support.get_frontmost_pid()
        assert isinstance(pid, int)
        assert pid > 0

    def test_axenabled(self):
        assert isinstance(support.axenabled(), bool)


@pytest.fixture
def frontmost_app():
    pid = support.get_frontmost_pid()
    app_ref = a11y.AXUIElement.from_pid(pid)
    return app_ref


class TestAXUIElement:
    def test_init(self):
        a11y.AXUIElement()

    def test_app_ref_from_pid(self):
        pid = support.get_frontmost_pid()
        app_ref = a11y.AXUIElement.from_pid(pid)
        assert "Application" in str(app_ref.ref)

    def test_app_ref_from_system_object(self):
        app_ref = a11y.AXUIElement.systemwide()
        assert "System Wide" in str(app_ref.ref)

    def test_get_ax_attributes(self, frontmost_app):
        sut = frontmost_app._get_ax_attributes()
        assert isinstance(sut, list)
        assert "AXRole" in sut
        assert "AXWindows" in sut
        assert "AXChildren" in sut

    def test_basic_get_attr(self, frontmost_app):
        assert isinstance(frontmost_app.AXTitle, str)
        assert isinstance(frontmost_app.AXWindows, list)

    def test_dir_has_ref(self, frontmost_app):
        assert "ref" in dir(frontmost_app)
        assert "AXTitle" in dir(frontmost_app)
