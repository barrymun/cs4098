import junit.framework.*;
import javax.swing.JTree;
import javax.swing.tree.DefaultMutableTreeNode;

public class testACJU extends TestCase{

	private static displayPO dpo;
	private static ActionMap map;

	public static Test suite()
	{
        	return new TestSuite(testACJU.class);
	}

	public void testNext()
	{
		//boolean goodTimes = true;
		LinkNode tester;
		map.setToFirstAction(1);
		for (int i=0; i<17; i++)
		{
			tester=map.getNextActionDetails(1);
			assertTrue(tester != null);
			//if (tester == null)
			//	goodTimes=false;

		}
		//assertTrue(goodTimes);
	}


	public void testNextCheck()
	{
	        assertTrue(map.isNextOk(1) == false);
	}

	public void testNextAtLimit()
	{
	       assertTrue(map.getNextActionDetails(1) == null);
	}

	public void testPrev()
	{
		LinkNode tester;
		for (int i=0; i<17; i++)
		{
			tester = map.getPrevActionDetails(1);
			assertTrue(tester != null);
		}
	}

	public void testPrevCheck()
	{
		for (int i=0; i<17; i++)
		{
			map.getPrevActionDetails(1);
		}
 		assertTrue(map.isPrevOk(1) == false);

	}

	public void testPrevAtLimit()
	{

		for (int i=0; i<17; i++)
		{
			map.getPrevActionDetails(1);
		}
		assertTrue(map.getPrevActionDetails(1) == null);
	}

        public void testSetToFirst()
        {
            map.setToFirstAction(1);
            assertEquals(map.getCurrentAction(1).getAttribute("name"),"overview");
        
        }
        
        public void testBuildActionTree()
        {
            DefaultMutableTreeNode tester = map.buildActionTree();
            assertEquals(tester.getUserObject(), "Actions");
            tester = (DefaultMutableTreeNode)tester.getChildAt(1).getChildAt(0);
            assertEquals(tester.getUserObject(), "(1)overview");           
            
        }
	public void testParseActionString()
	{
		String tester="(0)hello";
		String result[]= map.parsePid(tester);
                assertEquals("0", result[0]);
                assertEquals("hello", result[1]);
	}
	public void testParseActionSelectionString()
	{
		String tester="(0)*Choose: test1; test3";
		String result[]= map.parsePid(tester);
                assertEquals("0", result[0]);
                assertEquals("test1", result[1]);
	}
        public void testEnterIteration()
	{
		String tester="(0)*Enter iteration at itertest.";
		String result[]= map.parsePid(tester);
                assertEquals("0", result[0]);
                assertEquals("itertest", result[1]);
	}
        public void testEndIteration()
	{
		String tester="(0)*Skip to itertest2.";
		String result[]= map.parsePid(tester);
                assertEquals("0", result[0]);
                assertEquals("itertest2", result[1]);
	}
        public void testParseBadString()
	{
		String tester="(0*Choose: test1; test3";
		String result[]= map.parsePid(tester);
                
                assertNull(result);
	}
        
        public void testGetNextActionName()
        {
            map.getActionByName(0, "Fill_name");            
            LinkNode testNode=map.getCurrentLink(0);
            assertEquals(testNode.getNextActionName(),"No Valid Next Action");
        }
        
        public void testGetPostIterationActionName()
        {
            map.getActionByName(1,"create_baseline");
            LinkNode testNode=map.getCurrentLink(1);
            assertEquals("create_readme", testNode.getPostIterationActionName());
        }
        public void testIsNextActionReady()
        {            
            LinkNode testNode=map.getCurrentLink(1);
            assertFalse(testNode.isNextActionReady());
        }
        
	protected void setUp()
	{

		try {

			dpo = new displayPO("testfiles/blah.xml");
			dpo.convertDOM(1);
			map = dpo.getActions();

		}
		catch(Exception e)
		{
			System.err.println(e);
		}
	}
	
	public static void main(String[] args)
	{
		junit.textui.TestRunner.run(suite());
	}
}
