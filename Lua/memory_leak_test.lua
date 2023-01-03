function f1( options )
	print (options.name);
	return nil;
end

function f2( options )
	local action = function ()
		print (options.name);
	end
	return action;
end

function test1()
	io.write("======= test 1 =======\n");
	local options = { name = "option1"};
	setmetatable ( options, {__gc = function (o)
		io.write ( "Destroy handler for options with name '", o.name, "'\n" );
	end } );
	-- Don't create a closure
	local a = f1 ( options );
	io.write ( "Destroy options. No captures\n" );
	options = nil;
	io.write ( "Collect the garbage\n" );
	collectgarbage ();
	io.write ( "Garbage collected\n" );
	io.write ( "==========================\n\n");
end

function test2()
	io.write ( "======= test 2 =======\n" );
	local options = {
		name = "option1",
	};
	setmetatable ( options, {__gc = function (o)
		io.write ( "Destroy handler for options with name '", o.name, "'\n" );
	end } );
	-- Create a closure that holds a reference to the options table, not only options.name
	local a = f2 ( options );
	io.write ( "Captured options. Destroy options\n" );
	options = nil;
	io.write ( "Collect the garbage\n" );
	collectgarbage ();
	io.write ( "Garbage collected\n" );
	io.write ( "==========================\n\n");
end

test1 ();
test2 ();
