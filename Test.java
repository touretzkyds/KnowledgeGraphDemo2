import java.util.logging.Logger;

public class Test {
  static Logger log = Logger.getLogger(Test.class.getName());

  public static void init() {
    log.info("Test is loaded");
  }
}
